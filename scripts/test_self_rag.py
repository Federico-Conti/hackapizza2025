 
from typing import Any, Dict, List, Annotated, Sequence, TypedDict, Literal

from fastapi import  WebSocket

from langgraph.graph import END, StateGraph, START
#from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub

from app.utils.logger import logger
from app.schemas.ai import AIVectorSchema
from app.chatbot.base_rag import BaseRAG

# Grade Document
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

# Grade Hallucinations
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

# Grade Answer
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    max_retry: int
    question: str
    generation: str
    documents: List[str]


class BaseSelfRAG(BaseRAG):

    def __init__(self, data: AIVectorSchema, websocket: WebSocket = None, tracing: bool = False, sync: bool = False):
        super().__init__(data, tracing, sync, websocket)

        self.retrieval_grader = self.retrieval_grade_chain(self.llm)
        self.rag = self.rag_chain(self.llm)
        self.hallucination_grader = self.hallucination_grade_chain(self.llm)
        self.answer_grader = self.answer_grade_chain(self.llm)
        self.rewriter_grader = self.question_rewriter_chain(self.llm)

        # Create the graph
        workflow = StateGraph(GraphState)

        # Define the nodes
        workflow.add_node("retrieve", self.retrieve)  # retrieve
        workflow.add_node("grade_documents", self.grade_documents)  # grade documents
        workflow.add_node("generate", self.generate)  # generate
        workflow.add_node("generate_no_answer", self.generate_no_answer)  # generate non answer
        workflow.add_node("transform_query", self.transform_query)  # transform_query

        # Build graph
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_edge("generate_no_answer", END)
        workflow.add_conditional_edges(
            "grade_documents",
            self.decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
                "no_answer": "generate_no_answer",
            },
        )
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_conditional_edges(
            "generate",
            self.grade_generation_v_documents_and_question,
            {
                "not supported": "generate",
                "useful": END,
                "not useful": "transform_query",
            },
        )

        # Compile
        self.graph = workflow.compile()

    def retrieval_grade_chain(self, llm):
        """Binary score for relevance check on retrieved documents."""

        binary_score: str = Field(
            description="Documents are relevant to the question, 'yes' or 'no'"
        )

        logger.info(f"Creating grade chain ....")

        # LLM with function call
        structured_llm_grader = llm.with_structured_output(GradeDocuments)

        # Prompt
        system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
            It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
            If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
        grade_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
            ]
        )

        return grade_prompt | structured_llm_grader

    def rag_chain(self, llm):

        # Prompt
        prompt = hub.pull("rlm/rag-prompt")

        # Chain
        return prompt | llm | StrOutputParser()

    def hallucination_grade_chain(self, llm):

        structured_llm_grader = llm.with_structured_output(GradeHallucinations)

        # Prompt
        system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
            Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
        hallucination_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
            ]
        )

        return hallucination_prompt | structured_llm_grader

    def answer_grade_chain(self, llm):

        structured_llm_grader = llm.with_structured_output(GradeAnswer)

        # Prompt
        system = """You are a grader assessing whether an answer addresses / resolves a question \n 
            Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
            ]
        )

        return answer_prompt | structured_llm_grader

    def question_rewriter_chain(self, llm):

        # Prompt
        system = """You a question re-writer that converts an input question to a better version that is optimized \n 
            for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
        re_write_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                (
                    "human",
                    "Here is the initial question: \n\n {question} \n Formulate an improved question.",
                ),
            ]
        )

        return re_write_prompt | llm | StrOutputParser()

    ### Nodes

    def retrieve(self, state):
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        logger.debug("---RETRIEVE---")
        question = state["question"]

        # Retrieval
        #documents = self.vectorstore_retriever.get_relevant_documents(question)
        documents = self.vectorstore_retriever.invoke(question)
        return {"documents": documents, "question": question}

    def generate(self, state):
        """
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        logger.debug("---GENERATE---")
        question = state["question"]
        documents = state["documents"]

        # RAG generation
        generation = self.rag.invoke({"context": documents, "question": question})
        return {"documents": documents, "question": question, "generation": generation}

    def generate_no_answer(self, state):
        """
        Generate non content answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        logger.debug("---GENERATE NO ANSWER---")
        question = state["question"]
        documents = state["documents"]

        return {"documents": documents, "question": question, "generation": "I don't know the answer"}

    def grade_documents(self, state):
        """
        Determines whether the retrieved documents are relevant to the question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates documents key with only filtered relevant documents
        """

        logger.debug("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]
        max_retry = state["max_retry"]

        # Score each doc
        filtered_docs = []
        for d in documents:
            score = self.retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            logger.debug(f"---SCORE: {score}---")
            if score == None:
                logger.debug("---GRADE: DOCUMENT NOT RELEVANT---")
                continue

            grade = score.binary_score
            if grade == "yes":
                logger.debug("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                logger.debug("---GRADE: DOCUMENT NOT RELEVANT---")
                continue

        max_retry -= 1
        return {"documents": filtered_docs, "question": question, "max_retry": max_retry}

    def transform_query(self, state):
        """
        Transform the query to produce a better question.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Updates question key with a re-phrased question
        """

        logger.debug("---TRANSFORM QUERY---")
        question = state["question"]
        documents = state["documents"]

        # Re-write question
        better_question = self.rewriter_grader.invoke({"question": question})
        return {"documents": documents, "question": better_question}


    ### Edges

    def decide_to_generate(self, state):
        """
        Determines whether to generate an answer, or re-generate a question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Binary decision for next node to call
        """

        logger.debug("---ASSESS GRADED DOCUMENTS---")
        state["question"]
        filtered_documents = state["documents"]
        max_retry = state["max_retry"]

        if not filtered_documents:
            # All documents have been filtered check_relevance
            # We will re-generate a new query
            logger.debug(
                "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
            )

            if max_retry == 0:
                return "no_answer"
            else:
                return "transform_query"
        else:
            # We have relevant documents, so generate answer
            logger.debug("---DECISION: GENERATE---")
            return "generate"


    def grade_generation_v_documents_and_question(self, state):
        """
        Determines whether the generation is grounded in the document and answers question.

        Args:
            state (dict): The current graph state

        Returns:
            str: Decision for next node to call
        """

        logger.debug("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = self.hallucination_grader.invoke(
            {"documents": documents, "generation": generation}
        )
        grade = score.binary_score
        logger.debug(f"---HALLUCINATION GRADER: {grade}")

        # Check hallucination
        if grade == "yes":
            logger.debug("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
            # Check question-answering
            logger.debug("---GRADE GENERATION vs QUESTION---")
            score = self.answer_grader.invoke({"question": question, "generation": generation})
            grade = score.binary_score
            if grade == "yes":
                logger.debug("---DECISION: GENERATION ADDRESSES QUESTION---")
                return "useful"
            else:
                logger.debug("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                return "not useful"
        else:
            logger.debug("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
            return "not supported"
   
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)

response = llm.invoke("In one sentence, explain what ExamGuard does.")

print(response.content)
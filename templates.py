from langchain.prompts import ChatPromptTemplate

action_classification_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that can help write invoices and check them."),
        ("human", "Classify the intent of this prompt as either 'write_invoice' or 'check_invoice' or 'other': {prompt}"),
    ]
)

write_invoice_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that specializeds in writing invoices. Use the following instructions to write an invoice. This guide will give you the formatting guidelines and some other important rules you need to abide by: {instructions}"),
        ("human", "User wants to write this: {prompt}"),
    ]
)

check_invoice_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that specializeds in checking invoices. Use the following instructions to check an invoice. This guide will give you the formatting guidelines and some other important rules you need to abide by: {instructions}"),
        ("human", "User wants to check this: {prompt}"),
    ]
)

clarify_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant who can write and check invoices. You are given a user prompt and you need to clarify it to be more specific and clear on what the user wants. You will also need to ask for more information if needed."),
        ("human", "Original prompt: {prompt}"),
    ]
)


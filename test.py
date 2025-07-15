from gradio_client import Client

client = Client("Dhahlan2000/dechat_space_zero")
result = client.predict(
		message="Hello!!",
		system_message="You are a friendly Chatbot.",
		max_tokens=512,
		temperature=0.7,
		top_p=0.95,
		api_name="/chat"
)
print(result)
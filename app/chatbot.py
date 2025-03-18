import google.generativeai as genai
from flask import current_app

class AIChatbotService:
    def __init__(self):
        self.conversation = None
        
    def initialize_api(self):
        """Initialize the Gemini API with the API key from config"""
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        
        # Define generation config
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # Define safety settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Create a new conversation
        self.conversation = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        ).start_chat(
            history=[
                {
                    "role": "user",
                    "parts": ["I need help finding AI learning resources and answering questions about machine learning."]
                },
                {
                    "role": "model",
                    "parts": ["Hello! I'm your AI learning assistant. I can help you find resources for learning about AI and machine learning, recommend tutorials, explain concepts, suggest GitHub repositories, and answer questions about the field. How can I assist you today?"]
                }
            ]
        )
    
    def get_response(self, user_message):
        """Get a response from the Gemini API"""
        if not self.conversation:
            self.initialize_api()
            
        try:
            # Send the user message and get a response
            response = self.conversation.send_message(user_message)
            
            # Return the response text
            return response.text
        
        except Exception as e:
            print(f"Error calling Gemini API: {str(e)}")
            return "I'm having trouble connecting right now. Please try again later."
    
    def clear_history(self):
        """Clear the conversation history by reinitializing"""
        self.conversation = None
        self.initialize_api()

# Initialize the service for use in routes
chatbot_service = AIChatbotService()

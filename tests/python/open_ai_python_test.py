# pip install -U openai
import os
import unittest
from openai import OpenAI


class TestOpenAIProxy(unittest.TestCase):
    
    def setUp(self):
        """Set up the OpenAI client for testing"""
        self.client = OpenAI(
            base_url="http://127.0.0.1:8787/openai/v1",
            api_key=""  # The dummy key must always be empty, the proxy will inject the real API key
        )
        self.prompt = "Write a one-sentence greeting from moodys."
    
    def test_openai_proxy_chat_completion(self):
        """Test that the OpenAI proxy correctly handles chat completion requests"""
        print("Testing OpenAI proxy at http://127.0.0.1:8787...")
        print(f"Prompt: {self.prompt}")
        print("Sending request...")
        
        try:
            # Use standard OpenAI chat completions API
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": self.prompt}
                ],
                max_tokens=100
            )

            # Extract the response text
            text = resp.choices[0].message.content
            print("\nResponse:")
            print(text)
            
            # Assertions to verify the response
            self.assertIsNotNone(resp, "Response should not be None")
            self.assertIsNotNone(resp.choices, "Response should have choices")
            self.assertTrue(len(resp.choices) > 0, "Response should have at least one choice")
            self.assertIsNotNone(text, "Response text should not be None")
            self.assertTrue(len(text.strip()) > 0, "Response text should not be empty")
            
        except Exception as e:
            self.fail(f"Error connecting to proxy: {e}\nMake sure the proxy server is running with: ./run_local.sh")

    def test_openai_proxy_model_list(self):
        """Test that the OpenAI proxy correctly handles model list requests"""
        print("Testing OpenAI proxy model list at http://127.0.0.1:8787...")
        print("Sending models.list() request...")
        
        try:
            # Get list of available models
            models = self.client.models.list()
            
            print(f"\nFound {len(models.data)} models:")
            for model in models.data:
                print(f"  - {model.id}")
            
            # Assertions to verify the models response
            self.assertIsNotNone(models, "Models response should not be None")
            self.assertIsNotNone(models.data, "Models should have data")
            self.assertTrue(len(models.data) > 0, "Should have at least one model available")
            
            # Check that each model has an id
            for model in models.data:
                self.assertIsNotNone(model.id, "Each model should have an id")
                self.assertTrue(len(model.id.strip()) > 0, "Model id should not be empty")
                
        except Exception as e:
            self.fail(f"Error connecting to proxy for models list: {e}\nMake sure the proxy server is running with: ./run_local.sh")


if __name__ == "__main__":
    unittest.main()
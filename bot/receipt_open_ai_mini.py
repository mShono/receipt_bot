from dotenv import load_dotenv
import logging
import os
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_TOKEN"))

def open_ai_mini(text):
    try:
        logging.info(f"Product identifing launched")
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer",
                "content": f"""You are an AI that extracts product names and prices from receipt text. 
                            If the text is in finnish, product names need to be translated to english. You also need to shorten long product names to a short one 
                            that conveys the essence, and figure out which words were shortened, for example: 
                            'cherry tomatoes' instead of 'Luumukirsikkatomatti', 'chicken mince' instead of 'Kanamestari kanan jauhel',
                            'oat drink' instead of 'Vemondo luomu kaurajuoma'.
                            There also will be some products, which names are difficult to recognize - leave them as they are. 
                            Exampe: "Vemondo Luomu mantelij. sokt"
                            Under the product names, it can be written how many servings of the product were purchased at what price, 
                            for example: 3 x 2,95 EUR
                            The price is where the The price is where there is a designation EUR or €. 
                            You should give me the price for the total ammount of product, in the above example it is 8,85.
                            If underneath the product there's an information about discount, you should return the product price considering the discount.
                            Here’s the receipt data:
                            "{text}"
                            Return the data as a JSON array of products with their prices, like this:
                            [{{'name': "Product1", "price": 9.99}}, {{"name": "Product2", "price": 4.50}}]
                            Don't give me any additional information, text, formating, just the JSON array"""
                }
            ]
        )
    except Exception as e:
        logging.error(f"Product identifing with OpenAI failed: {e}")
        return None

    return completion.choices[0].message.content

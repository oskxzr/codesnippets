# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate(user_input):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_input),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["answers"],
            properties = {
                "answers": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["code", "language"],
                        properties = {
                            "code": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "language": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                        },
                    ),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(text="""You are an AI that returns code snippets. You will be given a request for a snippet. Respond with an array of answers. Each answer must contain the code (as a string) and the language (e.g. \"python\", \"javascript\"). Whatever language you supply must be directly compatible with Prism.js, a library used to render code in HTML. For example, instead of "text", "markdown". Instead of "js" or "JavaScript", "javascript".

Use native, built-in methods or standard library functions wherever possible. Do not re-implement built-in functionality.

Keep the code as brief and minimal as possible. If a one-liner is sufficient, return a one-liner. Avoid wrapping things in functions or classes unless the request specifically asks for it.

If there are multiple standard ways to solve it, return multiple answers.

Your response does NOT have to be one line. For readability, please include line breaks in your answer. Try to keep comments to a minimum.

Only return the JSON object matching this structure:

{
  \"answers\": [
    {
      \"code\": \"...\",
      \"language\": \"...\"
    }
  ]
}
No explanations, no extra text. Just the JSON.

"""),
        ],
    )

    text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        text += chunk.text
    return text
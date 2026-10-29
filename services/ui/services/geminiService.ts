
import { GoogleGenAI, Type } from "@google/genai";

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.warn("API_KEY environment variable not set. Using a mock response.");
}

const ai = API_KEY ? new GoogleGenAI({ apiKey: API_KEY }) : null;

// This function will call the Gemini API to generate deceptive URLs.
// It includes a mock response for environments where the API key is not available.
export async function generateDeceptiveUrls(prompt: string): Promise<string[]> {
  const fullPrompt = `Based on the following user prompt, generate 3 to 5 highly deceptive, realistic-looking URL paths. The goal is to create URLs that an attacker would find enticing to click on.
  
User Prompt: "${prompt}"

Return the response as a JSON object with a single key "urls" which is an array of strings. For example: {"urls": ["https://example.com/path1", "https://example.com/path2"]}.
`;
  
  if (!ai) {
    // Mock response if API key is not available
    console.log("Using mock Gemini response.");
    await new Promise(res => setTimeout(res, 1500)); // Simulate network delay
    const mockUrls = [
        `https://example.com/mock/${prompt.replace(/\s+/g, '-').toLowerCase()}/secret-data.zip`,
        `https://sharepoint.corp/sites/finance/docs/${prompt.replace(/\s+/g, '_')}_confidential.xlsx`,
        `https://api.internal.dev/backup/creds-for-${prompt.replace(/\s+/g, '')}.txt`,
    ];
    return mockUrls;
  }

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-pro",
      contents: fullPrompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
            type: Type.OBJECT,
            properties: {
                urls: {
                    type: Type.ARRAY,
                    items: {
                        type: Type.STRING
                    }
                }
            }
        },
        thinkingConfig: { thinkingBudget: 32768 }
      },
    });

    const responseText = response.text;
    const jsonResponse = JSON.parse(responseText);
    
    if (jsonResponse.urls && Array.isArray(jsonResponse.urls)) {
      return jsonResponse.urls;
    } else {
      throw new Error("Invalid JSON structure in response");
    }
  } catch (error) {
    console.error("Error calling Gemini API:", error);
    throw new Error("Failed to generate deceptive URLs from Gemini API.");
  }
}

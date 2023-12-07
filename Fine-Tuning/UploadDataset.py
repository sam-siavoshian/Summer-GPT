import openai
openai.api_key = "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"
response = openai.File.create(
  file=open("SummerDatasetV2.jsonl", "rb"),
  purpose='fine-tune'
)

print(response)
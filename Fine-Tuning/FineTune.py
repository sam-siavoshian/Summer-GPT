import openai
openai.api_key = "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"
file_id = "file-hpNFMEN1Gzc454DUOt9bFf79"
response = openai.FineTuningJob.create(training_file=file_id, model="gpt-3.5-turbo")
print(response)

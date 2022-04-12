from aitextgen import aitextgen

#ai = aitextgen(model_folder="trained_model", tokenizer_file="aiTextGen\aitextgen.tokenizer.json")
ai = aitextgen()

ai.generate()
ai.generate(n = 3, prompt='what did you train it on?', temperature=.8, max_length=1024)



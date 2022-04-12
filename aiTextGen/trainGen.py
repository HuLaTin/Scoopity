from aitextgen.TokenDataset import TokenDataset
from aitextgen.tokenizers import train_tokenizer
from aitextgen.utils import build_gpt2_config
from aitextgen import aitextgen

file_name = 'Data\lyricList.csv'

train_tokenizer(r'aiTextGen\Data\lyricList.csv')
tokenizer_file = "aitextgen.tokenizer.json"

#config = GPT2ConfigCPU()
config = build_gpt2_config(vocab_size=5000, max_length=32, dropout=0.0, n_embd=256, n_layer=8, n_head=8)# load custom gpt2 config
ai = aitextgen(tokenizer_file=tokenizer_file, config=config)
data = TokenDataset(file_name, tokenizer_file=tokenizer_file, block_size=64)
ai.train(data, batch_size=32, num_steps=150000, generate_every=5000, save_every=5000)


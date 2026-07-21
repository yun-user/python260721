from collections import defaultdict, OrderedDict
text = '''A press release is the quickest and easiest way to get free publicity. 
If well written, a press release can result in multiple published articles about your firm and its products. 
And that can mean new prospects contacting you asking you to sell to them. ...'''
text_splitted = text.lower().split() #다 소문자로 바꾼 후 공백을 기준으로 나눔
print(text_splitted)

word_count = defaultdict(int)
print(f'word_count: {word_count}')

for word in text_splitted:
    word_count[word] += 1
print(f'word_count: {word_count}')

def sort_by_key(items):
 return items[1]

word_count_sorted = sorted(
 word_count.items(), 
  key=sort_by_key, 
 reverse=True
)

print(f'word_count_sorted: {word_count_sorted}')

word_count_sorted_ordered = OrderedDict(word_count_sorted) 

print(f'word_count_sorted_ordered: {word_count_sorted_ordered}')

for k, v in word_count_sorted_ordered.items():
 print(f'word: {k}\tcount: {v}')

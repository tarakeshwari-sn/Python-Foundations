file=open("trial.txt","r")
content=file.read()
content=content.splitlines()
line_count,word_count=0,0

for line in content:
    line_count+=1
    word_count+=len(line.split())
print("Number of lines:",line_count)
print("Number of words:",word_count)

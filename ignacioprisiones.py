from bs4 import BeautifulSoup
import pandas as pd
import sys, re


#Reading the html file and converting into BeautifulSoup object
def get_data_from_file(file_path):
  with open(file_path, 'rb') as f:
    file = f.read()
  return BeautifulSoup(file, 'lxml')

#Removing Quiestion number and Option number text
def format_text(text):
  text = text.strip()
  if text.find(')') == -1 or text.find(')') > 4:
    if text.find('-') == -1 or text.find('-') > 4:
      return text[text.find('.') + 1::]
    return text[text.find('-') + 1::]
  return text[text.find(')')+1::]

#Extracting Questions with their Options
def get_quiz(data):
  data = data.find('body')
  quiz, solution, row = {}, [],  0
  number_of_answers = 0
  answer = 0
  errors = []
  #Looping through all the html elements in the body
  for line in data.find_all('p'):
    try:
      #Checking if the element contains text or not
      text = line.text
    except:
      #Doesnt contain text so we dont need it
      continue

    try:
      #Checking if the element is a Question/Option
      if not (text[0].isdigit() or text.startswith(
          ('a)', 'b)', 'c)', 'd)', 'A)', 'B)', 'C)', 'D)', 'A.', 'B.', 'C.', 'D.', 'a.', 'b.', 'c.', 'd.'))):
        continue
      #Special Case
      if text[0].isdigit() and len(text) < 5:
        continue
    except:
      #Isn't a Question/Option so we dont need it
      continue
    text = ''.join([x for x in text if x not in [';','<','"',',',':']])
    #Checking if the text is a Question/Solution or an Option
    if text[0].isdigit():
      if row != 0 and number_of_answers != 3:
        for _ in range(4 - number_of_answers):
          quiz[row].append('-')
          errors.append((row, quiz[row][0]))

      row += 1
      number_of_answers = 0
      quiz[row] = [format_text(text)]
      print('-----------')
      print(row, text)
    else:
      try:
        ans = line.find('span', {'style':re.compile('^font-weight:bold;*')})
        ans = ans.text.strip()
        if ans[0] not in ['a','b','c','d','A','B','C','D']:
          errors.append(('Solution', str(row) + ' ' + ans))
        solution.append(ans[0])
        print('sol', ans)
      except:
        pass
      number_of_answers += 1
      if number_of_answers > 3:
        continue
      quiz[row].append(format_text(text))
      print(row, text)

  print('-------')
  print('Errors')
  for a,b in errors:
    print(a,b)
  return quiz, solution

def make_csv(quiz, solution, parameter, output_name):
  #Making a DataFrame from the dictionary 'quiz'
  dff = pd.DataFrame.from_dict(quiz, orient = 'index')
  #Renaming the Colummns
  dff.columns = ['Question', 'Option A', 'Option B', 'Option C']
  #Adding Solution Column
  dff['Solution'] = solution
  dff['Parameter'] = parameter
  #Converting to csv file
  dff.to_csv('{}.csv'.format(output_name), index = False)
  print('File Made {}.csv'.format(output_name))
  dff.to_csv('{}.txt'.format(output_name), index = False, header = False, sep = ',')
  print('File Made {}.txt'.format(output_name))


if __name__ == '__main__':
  try:
    file_path = sys.argv[1]
    parameter = sys.argv[2] + '<'
  except:
    file_path = r'tema13guardiacivil.htm'
    parameter = '<'
  output_name = file_path[:file_path.find('.')]

  data = get_data_from_file(file_path)
  quiz, solution = get_quiz(data)
  print(len(quiz), len(solution))

  make_csv(quiz, solution, parameter, output_name)
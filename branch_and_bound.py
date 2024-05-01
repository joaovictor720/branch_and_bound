from sys import argv
from mip import *
import queue
import math


# resolve o modelo e mostra os valores das variáveis
def solve(model):
  status = model.optimize()

  if status != OptimizationStatus.OPTIMAL:
    return False

  print("Status = ", status)
  print(f"Solution value  = {model.objective_value:.2f}\n")
  
  print("Solution:")
  for v in model.vars:
      print(f"{v.name} = {v.x:.2f}")

  return True


# salva modelo em arquivo lp, e mostra o conteúdo
def save(model, filename):
  model.write(filename) # salva modelo em arquivo
  with open(filename, "r") as f: # lê e exibe conteúdo do arquivo
    print(f.read())

def readFile():
  model_file = open(argv[1], "r")
  model = Model(sense=MAXIMIZE, solver_name=CBC)

  # Lendo as dimensões do modelo
  aux = model_file.readline().strip().split()
  num_var = int(aux[0])
  num_rest = int(aux[1])

  # Define x como variáveis continuas restritas entre 0 e 1
  x = [model.add_var(var_type=CONTINUOUS, lb=0,ub=1, name=f"x_{i}") for i in range(num_var)]

  # Lendo os coeficientes da função objetivo
  aux = model_file.readline().strip().split()
  objective = 0
  for i in range(len(aux)):
    objective += int(aux[i]) * x[i]
  model.objective = objective

  # Lendo os coeficientes das restrições
  for i in range(num_rest):
    aux = model_file.readline().strip().split()
    lhs = 0
    for j in range(len(aux)-1):
      lhs += int(aux[j]) * x[j]
    model += lhs <= int(aux[len(aux)-1])

  return model


modelFather = readFile()
#save(modelFather, "teste.lp")
#solve(modelFather)

model_queue = queue.Queue()
model_queue.put(modelFather)
bestSolution = None

while True:

  if model_queue.empty():
    break
  # Retira o proximo da fila
  model = model_queue.get()

  # Resolve
  if solve(model) == False:
    continue

  closer05value = None
  minDistance = float('inf')
  i = 0

  for v in model.vars:
    distance = abs(v.x - 0.5)
    if distance < minDistance:
      minDistance = distance
      closer05value = i
    i = i+1

  if math.isclose(minDistance, 0.5, rel_tol=1e-9, abs_tol=0.0):
    print(model.objective_value)
    print("O programa está esperando por sua entrada...")
    entrada_usuario = input("Digite algo e pressione Enter para continuar: ")
    if bestSolution == None:
      bestSolution = model
    elif bestSolution.objective_value < model.objective_value:
      bestSolution = model
    else:
      continue
  elif bestSolution != None:
    if bestSolution.objective_value > model.objective_value:
      continue
  else:
    child2 = model.copy()
    child2 += child2.vars[closer05value] == 1
    
    model += model.vars[closer05value] == 0

    model_queue.put(model)
    model_queue.put(child2)


print("Resultado final")

solve(bestSolution)
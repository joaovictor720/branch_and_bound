from sys import argv
from mip import *
import queue

# Resolve o modelo e mostra os valores das variáveis
def solve(model):
  status = model.optimize()

  if status != OptimizationStatus.OPTIMAL:
    return False

  return True

# Exibe os valores do modelo
def print_model(model):
  print(f"Solution value = {model.objective_value:.2f}\n")
  print("Solution:")
  for v in model.vars:
      print(f"{v.name} = {v.x:.2f}")

# Salva modelo em arquivo lp, e mostra o conteúdo
def save(model, filename):
  model.write(filename) # salva modelo em arquivo
  with open(filename, "r") as f: # lê e exibe conteúdo do arquivo
    print(f.read())

# Lê o arquivo
def read_file(filename):
  model_file = open(filename, "r")
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

root = read_file(argv[1])

problem_queue = queue.Queue()
problem_queue.put(root)
best_int_solution = None

while True:

  if problem_queue.empty():
    break

  # Retirando o próximo da fila
  current_problem = problem_queue.get()

  # Resolvendo o subproblema
  is_feasible = solve(current_problem)

  # Podando por inviabilidade
  if not is_feasible:
    continue

  # Inicializando as variáveis auxiliares
  worst_var_index = None
  smallest_distance = float('inf')
  current_var_index = 0

  # Pegando a variável mais distante de ser binária de todas
  for v in current_problem.vars:
    distance = abs(v.x - 0.5)
    if distance < smallest_distance:
      smallest_distance = distance
      worst_var_index = current_var_index
    current_var_index = current_var_index+1

  # Verificando se a solução atual é inteira
  if smallest_distance == 0.5:
    # Atualizando a melhor solução inteira, caso o problema atual seja melhor que a melhor
    if best_int_solution == None:
      best_int_solution = current_problem
    elif best_int_solution.objective_value < current_problem.objective_value:
      best_int_solution = current_problem
    continue # Podando por achar uma solução inteira
  elif best_int_solution != None:
    if best_int_solution.objective_value > current_problem.objective_value:
      continue # Podando por achar uma solução pior do que a inteira atual

  # Ramificando em torno da pior variável (menos binária)
  child1 = current_problem.copy()
  child2 = current_problem.copy()
  
  child1 += child1.vars[worst_var_index] == 0
  child2 += child2.vars[worst_var_index] == 1

  problem_queue.put(child1)
  problem_queue.put(child2)

print("Resultado final")

print_model(best_int_solution)

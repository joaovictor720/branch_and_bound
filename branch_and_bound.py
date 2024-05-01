from sys import argv
from mip import *

# resolve o modelo e mostra os valores das variáveis
def solve(model):
  status = model.optimize()

  if status != OptimizationStatus.OPTIMAL:
    return

  print("Status = ", status)
  print(f"Solution value  = {model.objective_value:.2f}\n")
  
  print("Solution:")
  for v in model.vars:
      print(f"{v.name} = {v.x:.2f}")


# salva modelo em arquivo lp, e mostra o conteúdo
def save(model, filename):
  model.write(filename) # salva modelo em arquivo
  with open(filename, "r") as f: # lê e exibe conteúdo do arquivo
    print(f.read())

model_file = open(argv[1], "r")
model = Model(sense=MAXIMIZE, solver_name=CBC)

# Lendo as dimensões do modelo
aux = model_file.readline().strip().split()
num_var = int(aux[0])
num_rest = int(aux[1])

x = [model.add_var(var_type=CONTINUOUS, lb=0, name=f"x_{i}") for i in range(num_var)]

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

save(model, "teste.lp")
solve(model)

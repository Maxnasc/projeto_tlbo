import copy
import random
import math
import statistics

def get_opposite(base, top, xi):
    return (top + base) - xi

def initialize(m, data_config, opposition):
    x1_base, x1_top = data_config["range"]["x1"]["base"], data_config["range"]["x1"]["top"]
    x2_base, x2_top = data_config["range"]["x2"]["base"], data_config["range"]["x2"]["top"]

    if opposition:
        x = []
        for _ in range(m // 2):
            xa1 = random.uniform(x1_base, x1_top)
            xa2 = random.uniform(x2_base, x2_top)
            xb1 = get_opposite(x1_base, x1_top, xa1)
            xb2 = get_opposite(x2_base, x2_top, xa2)
            x.extend([[xa1, xa2], [xb1, xb2]])
        return x
    else:
        return [[random.uniform(x1_base, x1_top), random.uniform(x2_base, x2_top)] for _ in range(m)]

def shubert(x1, x2):
    sum1 = sum(i * math.cos((i + 1) * x1 + i) for i in range(1, 6))
    sum2 = sum(i * math.cos((i + 1) * x2 + i) for i in range(1, 6))
    return sum1 * sum2

def camel(x1, x2):
    term1 = (4 - 2.1 * x1**2 + x1**4 / 3) * x1**2
    term2 = x1 * x2
    term3 = (-4 + 4 * x2**2) * x2**2
    return term1 + term2 + term3

def run_function(data_config, variables):
    problem = data_config["problem"]
    if problem == "shubert":
        return [(1 / (shubert(x[0], x[1]) + 200)) for x in variables]
    else:
        return [(1 / (camel(x[0], x[1]) + 200)) for x in variables]

def run_tlbo_flowchart(iterations, P, data_config, opposition):
    population = initialize(P, data_config, opposition)
    scores = run_function(data_config, population)

    best_global_individual = population[scores.index(max(scores))]
    best_global_score = max(scores)
    
    best_objective_values_per_iteration = [(1 / best_global_score) - 200]

    for _ in range(iterations):
        # Encontrar o professor da população atual
        teacher_index = scores.index(max(scores))
        teacher = population[teacher_index]
        mean_vector = [statistics.mean([ind[d] for ind in population]) for d in [0, 1]]

        new_population = []
        new_scores = []

        # Fase Professor
        for i in range(P):
            TF = random.choice([1, 2])
            # Criar um novo aluno baseado no professor e na média
            r_val = random.random()
            teacher_learner = [
                population[i][dim] + r_val * (teacher[dim] - TF * mean_vector[dim])
                for dim in [0, 1]
            ]
            
            # Garantir que os valores estejam dentro dos limites (Bound Checking)
            x1_base, x1_top = data_config['range']['x1']['base'], data_config['range']['x1']['top']
            x2_base, x2_top = data_config['range']['x2']['base'], data_config['range']['x2']['top']
            teacher_learner[0] = max(x1_base, min(x1_top, teacher_learner[0]))
            teacher_learner[1] = max(x2_base, min(x2_top, teacher_learner[1]))

            teacher_learner_score = run_function(data_config, [teacher_learner])[0]
            
            if teacher_learner_score > scores[i]: # Compara com o score do indivíduo original na população
                new_population.append(teacher_learner)
                new_scores.append(teacher_learner_score)
                if teacher_learner_score > best_global_score:
                    best_global_score = teacher_learner_score
                    best_global_individual = teacher_learner
            else:
                new_population.append(population[i]) # Mantém o indivíduo original se não houver melhoria
                new_scores.append(scores[i])


        # Atualiza a população e scores para a fase do aluno com os resultados da fase do professor
        population = new_population[:] # Use slicing para criar uma cópia
        scores = new_scores[:]


        # Fase Alunos
        for i in range(P):
            j = random.choice([idx for idx in range(P) if idx != i])

            r_val = random.random()
            if scores[i] > scores[j]:
                student_learner = [
                    population[i][dim] + r_val * (population[i][dim] - population[j][dim])
                    for dim in [0, 1]
                ]
            else:
                student_learner = [
                    population[i][dim] + r_val * (population[j][dim] - population[i][dim])
                    for dim in [0, 1]
                ]

            # Garantir que os valores estejam dentro dos limites (Bound Checking)
            student_learner[0] = max(x1_base, min(x1_top, student_learner[0]))
            student_learner[1] = max(x2_base, min(x2_top, student_learner[1]))

            student_learner_score = run_function(data_config, [student_learner])[0]

            if student_learner_score > scores[i]:
                population[i] = student_learner
                scores[i] = student_learner_score
                if student_learner_score > best_global_score:
                    best_global_score = student_learner_score
                    best_global_individual = student_learner
        
        best_objective_values_per_iteration.append((1/max(scores))-200)

    # Retorna o valor real da função objetivo para o melhor indivíduo encontrado
    return (1 / best_global_score) - 200, best_objective_values_per_iteration

def run_tlbo_pseudocode(iterations, P, data_config, opposition):
    population = initialize(P, data_config, opposition)
    scores = run_function(data_config, population)

    best_global_individual = population[scores.index(max(scores))]
    best_global_score = max(scores)
    
    best_objective_values_per_iteration = [(1 / best_global_score) - 200]

    for _ in range(iterations):
        # Encontrar o professor da população atual
        teacher_index = scores.index(max(scores))
        teacher = population[teacher_index]
        mean_vector = [statistics.mean([ind[d] for ind in population]) for d in [0, 1]]

        new_population = []
        new_scores = []

        # Fase Professor
        for i in range(P):
            TF = random.choice([1, 2])
            # Criar um novo aluno baseado no professor e na média
            r_val = random.random()
            teacher_learner = [
                population[i][dim] + r_val * (teacher[dim] - TF * mean_vector[dim])
                for dim in [0, 1]
            ]
            
            # Garantir que os valores estejam dentro dos limites (Bound Checking)
            x1_base, x1_top = data_config['range']['x1']['base'], data_config['range']['x1']['top']
            x2_base, x2_top = data_config['range']['x2']['base'], data_config['range']['x2']['top']
            teacher_learner[0] = max(x1_base, min(x1_top, teacher_learner[0]))
            teacher_learner[1] = max(x2_base, min(x2_top, teacher_learner[1]))

            teacher_learner_score = run_function(data_config, [teacher_learner])[0]
            
            if teacher_learner_score > scores[i]: # Compara com o score do indivíduo original na população
                new_population.append(teacher_learner)
                new_scores.append(teacher_learner_score)
                if teacher_learner_score > best_global_score:
                    best_global_score = teacher_learner_score
                    best_global_individual = teacher_learner
                # Fase Alunos
                for i in range(P):
                    j = random.choice([idx for idx in range(P) if idx != i])

                    r_val = random.random()
                    if scores[i] > scores[j]:
                        student_learner = [
                            population[i][dim] + r_val * (population[i][dim] - population[j][dim])
                            for dim in [0, 1]
                        ]
                    else:
                        student_learner = [
                            population[i][dim] + r_val * (population[j][dim] - population[i][dim])
                            for dim in [0, 1]
                        ]

                    # Garantir que os valores estejam dentro dos limites (Bound Checking)
                    student_learner[0] = max(x1_base, min(x1_top, student_learner[0]))
                    student_learner[1] = max(x2_base, min(x2_top, student_learner[1]))

                    student_learner_score = run_function(data_config, [student_learner])[0]

                    if student_learner_score > scores[i]:
                        population[i] = student_learner
                        scores[i] = student_learner_score
                        if student_learner_score > best_global_score:
                            best_global_score = student_learner_score
                            best_global_individual = student_learner
                    
            else:
                new_population.append(population[i]) # Mantém o indivíduo original se não houver melhoria
                new_scores.append(scores[i])

        # Atualiza a população e scores para a fase do aluno com os resultados da fase do professor
        population = new_population[:] # Use slicing para criar uma cópia
        scores = new_scores[:]
        
        best_objective_values_per_iteration.append((1/max(scores))-200)

    # Retorna o valor real da função objetivo para o melhor indivíduo encontrado
    return (1 / best_global_score) - 200, best_objective_values_per_iteration

if __name__ == "__main__":
    data_config = {
        "problem": "shubert",
        "range": {
            "x1": {"base": -10, "top": 10},
            "x2": {"base": -10, "top": 10},
        },
    }
    # score, scores = run_tlbo_flowchart(iterations=30, P=100, data_config=data_config, opposition=False)
    score, scores = run_tlbo_pseudocode(iterations=30, P=100, data_config=data_config, opposition=False)
    print(score)

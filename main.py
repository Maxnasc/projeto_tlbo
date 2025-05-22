import ast
import pandas as pd
import matplotlib.pyplot as plt
import itertools
import statistics

from tlbo_algorithm import run_tlbo_flowchart, run_tlbo_pseudocode


def get_result_and_plot(generations, m, data_config, opposition, function_key, config_code):
    all_results = []
    all_scores_g = []
    best_result = None
    best_score = float('inf')  # ou float('-inf') dependendo se você minimiza ou maximiza

    if function_key == 'flowchart':
        for i in range(30):
            result, scores_g = run_tlbo_flowchart(iterations=generations, P=m, data_config=data_config, opposition=opposition)
            all_results.append(result)
            all_scores_g.append(scores_g)

            if result < best_score:  # Assumindo que você está minimizando
                best_score = result
                best_result = result
    else:
        for i in range(30):
            result, scores_g = run_tlbo_pseudocode(iterations=generations, P=m, data_config=data_config, opposition=opposition)
            all_results.append(result)
            all_scores_g.append(scores_g)

            if result < best_score:  # Assumindo que você está minimizando
                best_score = result
                best_result = result

    # Cálculo da média dos scores_g ao longo das execuções para cada geração
    if all_scores_g:
        num_generations = len(all_scores_g[0])
        mean_scores_g = [statistics.median(scores[g] for scores in all_scores_g) for g in range(num_generations)]
    else:
        mean_scores_g = []

    print(f'Melhor resultado médio configuração {config_code} - {data_config.get("problem")}: {best_result}')

    return {
        "best_result": best_result,
        "mean_scores_g": mean_scores_g,
        "opposition": opposition,
        'function_key': function_key,
        "generations": generations,
        "m": m,
        "problem": data_config.get("problem")
    }

def your_function_to_track():
    generations = 30
    m = 100
    data_config = {
        "problem": "shubert",
        "range": {
            "x1": {"base": -10, "top": 10},
            "x2": {"base": -10, "top": 10},
        },
        "v_max": {
            "x1": {"min": -1, "max": 1},
            "x2": {"min": -1, "max": 1},
        },
    }
    all_results = []
    oppositions = [True, False]
    function_keys = ['flowchart', 'pseudocode']

    config_counter = 1

    for problem, target in {"shubert": -186.7309, "camel": -1.0316}.items():
        data_config["problem"] = problem
        for opposition, function_key in itertools.product(oppositions, function_keys):
            print(f"Rodando: prob={problem}, gen={generations}, m={m}, opp={opposition}, function_key={function_key}, config={config_counter}")
            result_dict = get_result_and_plot(generations, m, data_config, opposition, function_key, config_counter)
            all_results.append(result_dict)
            config_counter += 1

    # Criar um único DataFrame com todos os dados
    df = pd.DataFrame(all_results)
    df_grouped = df.groupby("problem")
    for problem, data in df_grouped:
        plt.figure(figsize=(8, 5))
        plt.boxplot(data["mean_scores_g"], patch_artist=True)
        plt.title(f"Boxplot dos Melhores Scores por Configuração - {problem}")
        plt.ylabel("Melhor Score")
        plt.xlabel("Configurações")
        plt.grid(True)
        plt.xticks(
            range(1, len(data) + 1),
            [f"Fun.={r['function_key']} Opp={r['opposition']}" for _, r in data.iterrows()],
            rotation=45,
            ha="right"
        )
        plt.tight_layout()
        plt.savefig(f'images/boxplot_configuracoes_{problem}.png')

    # === Identificar os melhores resultados
    best_shubert = df[df["problem"] == "shubert"].sort_values(by="best_result").iloc[0]
    print('Melhor Shubert:')
    print(best_shubert.drop(columns=['mean_scores']))
    best_shubert.to_csv('melhores_fitness_shubert_tlbo.csv')
    best_camel = df[df["problem"] == "camel"].sort_values(by="best_result").iloc[0]
    print('Melhor Camel:')
    print(best_camel.drop(columns=['mean_scores']))
    best_camel.to_csv('melhores_fitness_camel_tlbo.csv')

    # === Leitura dos dados do GA
    try:
        df_ga_shubert_GA = pd.read_csv("previous_results/melhores_fitness_shubert_GA.csv", header=None)
        df_ga_camel_GA = pd.read_csv("previous_results/melhores_fitness_camel_GA.csv", header=None)
        df_ga_shubert_PSO = pd.read_csv("previous_results/melhores_fitness_shubert_PSO.csv", header=None)
        df_ga_camel_PSO = pd.read_csv("previous_results/melhores_fitness_camel_PSO.csv", header=None)
        df_ga_shubert_de = pd.read_csv("previous_results/melhores_fitness_shubert_de.csv", header=None)
        df_ga_camel_de = pd.read_csv("previous_results/melhores_fitness_camel_de.csv", header=None)
        df_ga_shubert_clonalg = pd.read_csv("previous_results/melhores_fitness_shubert_clonalg.csv", header=None)
        df_ga_camel_clonalg = pd.read_csv("previous_results/melhores_fitness_camel_clonalg.csv", header=None)

        # === Gráfico de comparação SHUBERT
        plt.figure(figsize=(8, 5))
        plt.axhline(y=-186.7309, color="r", linestyle="--", label="Valor esperado (target)")
        plt.plot(range(1, len(best_shubert["mean_scores_g"]) + 1), best_shubert["mean_scores_g"], 'o-', label=f"TLBO (Function={best_shubert['function_key']}, Opp={best_shubert['opposition']})", color="blue")
        plt.plot(ast.literal_eval(df_ga_shubert_GA.iloc[7].values[1]), 'x-', label="GA", color="green")
        plt.plot(ast.literal_eval(df_ga_shubert_PSO.iloc[4].values[1]), 'x-', label="PSO", color="orange")
        plt.plot(ast.literal_eval(df_ga_shubert_de.iloc[1].values[1]), 'x-', label="DE", color="red")
        plt.plot(ast.literal_eval(df_ga_shubert_clonalg.iloc[2].values[1]), 'x-', label="CLONALG", color="black")
        plt.title("Comparação da evolução dos algoritmos - Shubert")
        plt.xlabel("Gerações")
        plt.ylabel("Score")
        plt.legend()
        plt.grid(True)
        plt.savefig('images/comparation_shubert_de.png')

        # === Gráfico de comparação CAMEL
        plt.figure(figsize=(8, 5))
        plt.axhline(y=-1.0316, color="r", linestyle="--", label="Valor esperado (target)")
        plt.plot(range(1, len(best_camel["mean_scores_g"]) + 1), best_camel["mean_scores_g"], 'o-', label=f"TLBO (Function={best_shubert['function_key']}, Opp={best_camel['opposition']})", color="blue")
        plt.plot(ast.literal_eval(df_ga_camel_GA.iloc[7].values[1]), 'x-', label="GA", color="green")
        plt.plot(ast.literal_eval(df_ga_camel_PSO.iloc[4].values[1]), 'x-', label="PSO", color="orange")
        plt.plot(ast.literal_eval(df_ga_camel_de.iloc[1].values[1]), 'x-', label="DE", color="red")
        plt.plot(ast.literal_eval(df_ga_camel_clonalg.iloc[2].values[1]), 'x-', label="CLONALG", color="black")
        plt.title("Comparação da evolução dos algoritmos - Camel")
        plt.xlabel("Gerações")
        plt.ylabel("Score")
        plt.legend()
        plt.grid(True)
        plt.ylim(-2.0, 0.0)
        plt.savefig('images/comparation_camel_de.png')
    except FileNotFoundError:
        print("Arquivos 'melhores_fitness_shubert.csv' ou 'melhores_fitness_camel.csv' não encontrados para comparação com GA.")

    plt.show()

if __name__ == "__main__":
    your_function_to_track()
    
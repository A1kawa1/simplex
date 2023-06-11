from django.shortcuts import render
from django.shortcuts import redirect
import numpy as np
import json
from dataclasses import dataclass

from .solver_max import canonization
from .solver_max import simplex_method as simplex_method_max
from .solver_min import simplex_method as simplex_method_min


@dataclass
class Result:
    str_res: list
    mark: list


def home(request):
    count_var = request.GET.get('count_var', '')
    count_cond = request.GET.get('count_cond', '')
    if not all([count_var, count_cond]):
        return render(request, 'home.html')
    try:
        count_var = int(count_var)
        count_cond = int(count_cond)
    except:
        return render(request, 'home.html')
    return redirect('solve:inp_data', count_var, count_cond)


def inp_data(request, count_var, count_cond):
    names = [f'x{el+1}' for el in range(count_var)]
    conds = [f'cond{el+1}' for el in range(count_cond)]

    var_coef = [request.GET.get(el, '') for el in names]
    cond_coef = [
        [request.GET.get(f'{el}-{el_x}', '') for el_x in names]
        for el in conds
    ]
    cond_res = [request.GET.get(f'{el}-res', '') for el in conds]

    if not all(var_coef+cond_coef+cond_res):
        return render(
            request,
            'inp_data.html',
            {
                'names': names,
                'conds': conds
            }
        )

    try:
        var_coef = list(map(int, var_coef))
        cond_coef = [list(map(int, j)) for j in cond_coef]
        cond_res = list(map(int, cond_res))
    except:
        print('ошибка')
        return render(
            request,
            'inp_data.html',
            {
                'names': names,
                'conds': conds
            }
        )

    data = {
        'var_coef': var_coef,
        'cond_coef': cond_coef,
        'cond_res': cond_res
    }
    with open('data.json', 'w') as file:
        json.dump(data, file)

    return redirect('solve:result')


def result(request):
    with open('data.json') as file:
        try:
            data = json.load(file)
            C = np.array(data.get('var_coef'))
            B = np.array([data.get('cond_res')], dtype=np.float)
            A = np.array(data.get('cond_coef'), dtype=np.float)

            mat, fun, bas = canonization(A, B, C)
            x_max, res_max = simplex_method_max(mat, fun, bas, C)

            with open('result.json') as file_res:
                data_res = json.load(file_res)
                res_matrix_max = []

                for string, mark in zip(data_res.get('matrix'), data_res.get('mark')):
                    res_matrix_max.append(
                        Result(
                            string,
                            mark
                        )
                    )
                print(*res_matrix_max, sep='\n')

            mat, fun, bas = canonization(A, B, C)
            x_min, res_min = simplex_method_min(mat, fun, bas, C)

            with open('result.json') as file_res:
                data_res = json.load(file_res)
                res_matrix_min = []

                for string, mark in zip(data_res.get('matrix'), data_res.get('mark')):
                    res_matrix_min.append(
                        Result(
                            string,
                            mark
                        )
                    )
                print(*res_matrix_min, sep='\n')

            return render(
                request,
                'result.html',
                {
                    'x_max': x_max,
                    'x_min': x_min,
                    'res_max': res_max,
                    'res_min': res_min,
                    'result_max': res_matrix_max,
                    'result_min': res_matrix_min,
                    'len': len(x_max)+1
                }
            )
        except:
            return redirect('solve:inp_data', len(C), len(B[0]))

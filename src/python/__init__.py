"""python package.

Python 代码
"""

from functools import partial
import inspect

from bigmodule import I

# metadata
# 模块作者
author = "BigQuant"
# 模块分类
category = "通用"
# 模块显示名
friendly_name = "Python函数"
# 文档地址, optional
doc_url = "https://bigquant.com/wiki/"
# 是否自动缓存结果
cacheable = True


DEFAULT_RUN = """def bigquant_run(input_1, input_2, input_3):
# Python 代码入口函数，input_1/2/3 对应三个输入端，data_1/2/3 对应三个输出端
# 示例代码如下。在这里编写您的代码
 
 
 
import dai
 
df = input_1.read()
ds = dai.DataSource.write_bdb(df)
 
return dict(data_1=ds, data_2={"hello": "world"}, data_3=None)
"""

DEFAULT_POST_RUN = """def bigquant_run(outputs):
    # 后处理函数，可选。输入是主函数的输出，可以在这里对数据做处理，或者返回更友好的outputs数据格式。此函数输出不会被缓存。
    return outputs
"""


def run(
    run: I.code("主函数，返回dict对象", I.code_python, default=DEFAULT_RUN, specific_type_name="函数", auto_complete_type="python",optional=False),
    do_run: I.bool("运行主函数，如果不运行主函数，将通过 data_1 返回函数 partial(run, input_*=input_*)") = True,
    post_run_outputs_: I.code(
        "后处理函数，输入是主函数的输出，此函数输出不会被缓存", I.code_python, default=DEFAULT_POST_RUN, specific_type_name="函数", auto_complete_type="python",optional=False
    ) = None,
    input_1: I.port("输入1，传入到函数的参数 input_1", optional=True) = None,
    input_2: I.port("输入2，传入到函数的参数 input_2", optional=True) = None,
    input_3: I.port("输入3，传入到函数的参数 input_3", optional=True) = None,
    m_meta_kwargs=None,
) -> [
    I.port("输出1，对应函数输出的 data_1", "data_1", optional=True),
    I.port("输出2，对应函数输出的 data_2", "data_2", optional=True),
    I.port("输出3，对应函数输出的 data_3", "data_3", optional=True),
]:
    """执行任意Python代码，支持缓存加速。"""

    if do_run:
        result = run(input_1, input_2, input_3)
        if result is None:
            raise Exception("The python run function's return value cannot be None")
        if not isinstance(result, dict):
            raise Exception("The python run function's return value must be a dict")
        if len(set(result.keys()) - {"data_1", "data_2", "data_3"}) > 0:
            raise Exception("The python run function's return value keys must be 'data_1', 'data_2', 'data_3'")
        outputs = I.Outputs(**result)
    else:
        kwargs = {}
        parameters = inspect.signature(run).parameters
        if "input_1" in parameters:
            kwargs["input_1"] = input_1
        if "input_2" in parameters:
            kwargs["input_2"] = input_2
        if "input_3" in parameters:
            kwargs["input_3"] = input_3
        if kwargs:
            run = partial(run, **kwargs)
        outputs = I.Outputs(data_1=run)

    return outputs


def post_run(outputs):
    if hasattr(outputs, "post_run_outputs_"):
        outputs = outputs.post_run_outputs_(outputs)
        del outputs.post_run_outputs_

    return outputs


def cache_key(kwargs):
    if not kwargs.get("do_run", True):
        # disable cache
        return None

    return kwargs

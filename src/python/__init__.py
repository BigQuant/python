"""python package.

Python code
"""

from functools import partial
import inspect

from bigmodule import I

# metadata
# Module author
author = "AFE"
# Module category
category = "General"
# Module display name
friendly_name = "Python function"
# Documentation URL, optional
doc_url = "wiki/"
# Whether to automatically cache results
cacheable = True


DEFAULT_RUN = """def bigquant_run(input_1, input_2, input_3):
    # Python code entry function, input_1/2/3 correspond to three input ports, data_1/2/3 correspond to three output ports
    # Sample code is as follows. Write your code here

    import dai

    df = input_1.read()
    ds = dai.DataSource.write_bdb(df)

    return dict(data_1=ds, data_2={"hello": "world"}, data_3=None)
"""

DEFAULT_POST_RUN = """def bigquant_run(outputs):
    # Post-processing function, optional. The input is the output of the main function, and you can process the data here or return a more user-friendly outputs data format. The output of this function will not be cached.
    return outputs
"""


def run(
    run: I.code("Main function, returns a dict object", I.code_python, default=DEFAULT_RUN, specific_type_name="function", auto_complete_type="python"),
    do_run: I.bool("Run the main function, if not running the main function, it will return the function partial(run, input_*=input_*)") = True,
    post_run_outputs_: I.code(
        "Post-processing function, input is the output of the main function, this function's output will not be cached", I.code_python, default=DEFAULT_POST_RUN, specific_type_name="function", auto_complete_type="python"
    ) = None,
    input_1: I.port("Input 1, passed as parameter input_1 to the function", optional=True) = None,
    input_2: I.port("Input 2, passed as parameter input_2 to the function", optional=True) = None,
    input_3: I.port("Input 3, passed as parameter input_3 to the function", optional=True) = None,
    m_meta_kwargs=None,
) -> [
    I.port("Output 1, corresponding to the function's output data_1", "data_1", optional=True),
    I.port("Output 2, corresponding to the function's output data_2", "data_2", optional=True),
    I.port("Output 3, corresponding to the function's output data_3", "data_3", optional=True),
]:
    """Execute arbitrary Python code with support for cache acceleration."""

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

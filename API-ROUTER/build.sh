rm -rf build dist mobigen_router.egg-info
pip uninstall mobigen_router -y

python setup.py bdist_wheel

pip install ./dist/mobigen_router-0.3-py3-none-any.whl



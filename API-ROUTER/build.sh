rm -rf build dist mobi_router.egg-info
pip uninstall mobi_router -y

python setup.py bdist_wheel

pip install ./dist/mobi_router-1.0-py3-none-any.whl



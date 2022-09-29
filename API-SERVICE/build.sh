rm -rf build dist mobigen_service.egg-info
pip uninstall mobigen_service -y

python setup.py bdist_wheel

pip install ./dist/mobigen_service-0.2-py3-none-any.whl



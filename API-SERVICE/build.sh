rm -rf build dist mobi_service.egg-info
pip uninstall mobi_service -y

python setup.py bdist_wheel

pip install ./dist/mobi_service-1.0-py3-none-any.whl



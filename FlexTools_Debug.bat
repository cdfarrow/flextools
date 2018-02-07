@echo off

pushd FlexTools

call ..\py_net FlexTools.py >..\error.log %*

popd

notepad error.log

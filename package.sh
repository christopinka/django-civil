#!/bin/bash

PWD=`pwd`

rm -Rf `find ./civil -name "*.pyc" | xargs`

cd ..
tar -cf django-civil.tar django-civil
p7zip django-civil.tar

cd $PWD

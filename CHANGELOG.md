# Changelog

## v1.0.0
Initial Release

## v1.0.1
Bug Fixes

- change ssize_t to long int
- update readme

## v1.0.2
Update manifest

- Change wheel build method

## v1.1.0
Multithreading

- Add support for mutlithreading the `Model` class
- Fix __len__ property 

## v1.1.1
Importlib Changes

- Change c module generation and use importlib to 
  dynamically import multiple simulink models
- Update test cases

## v1.1.2
Compatibility Updates

- Some models don't implement tFinal
- Support for not enabling mat file logging
- Added spinner during compile time
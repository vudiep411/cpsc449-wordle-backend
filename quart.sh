#!/bin/sh
chmod +xwr quart.sh
export QUART_APP=wordle:app
quart run
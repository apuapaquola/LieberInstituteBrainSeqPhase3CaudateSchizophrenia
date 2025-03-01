#!/bin/bash

FEATURE="exons"

Rscript ../_h/parallel_mashr.R --feature $FEATURE --run_chunk \
        --chunk_size 1000 --threads 6 1>$FEATURE/output.log 2>$FEATURE/error.log

#!/bin/bash

export PERL5LIB=/work/users/ngocnt/tools/vcftools/vcftools-vcftools-581c231/src/perl
java="/work/users/ngocnt/tools/java-8/bin/java"
TOOLS_PATH="/work/users/ngocnt/tools"
REF_PATH="/work/users/ngocnt/referencegenome"
dbSNP="/work/users/ngocnt/referencegenome/dbSNP/common_all_20180418.vcf"
humanref="/work/users/ngocnt/referencegenome/hg38.fa"
trimmomatic="$TOOLS_PATH/Trimmomatic-0.39/"
adapter="$trimmomatic/adapters/TruSeq3-PE.fa"
bwa="/work/users/ngocnt/tools/bwa-0.7.17/bwa"
gatk="$TOOLS_PATH/gatk-4.1.2.0/gatk"
picard="$TOOLS_PATH/picard119/picard-tools-1.119"
annovar_convert="$TOOLS_PATH/annovar/annovar/convert2annovar.pl"
annovar_annotate="$TOOLS_PATH/annovar/annovar/annotate_variation.pl"
humandb="/work/users/ngocnt/tools/annovar/annovar/humandb" 
G_REF="/work/users/ngocnt/referencegenome/hg38.fa"
vcftools="/work/users/ngocnt/tools/vcftools/vcftools-vcftools-581c231/bin/vcftools"
table_annovar="$TOOLS_PATH/annovar/annovar/table_annovar.pl"





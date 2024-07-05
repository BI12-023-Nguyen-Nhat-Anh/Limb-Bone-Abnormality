#/bin/bash

TOOLS_PATH="/home/student10"
annovar_convert="$TOOLS_PATH/annovar/convert2annovar.pl"
annovar_table="$TOOLS_PATH/annovar/table_annovar.pl"
humandb="$TOOLS_PATH/annovar/humandb"
annovar="$TOOLS_PATH/annovar/annotate_variation.pl"
sample_id=$1

echo "=============================="
echo "PREPARE INPUT FILE FOR ANNOVAR"
echo "=============================="

$annovar_convert -format vcf4 --includeinfo \
 ${sample_id}.SNPs.PASS.vcf -outfile ${sample_id}.SNPs.PASS.avinput

$annovar_convert -format vcf4 --includeinfo \
 ${sample_id}.indels.PASS.vcf -outfile ${sample_id}.indels.PASS.avinput

echo "=================="
echo "VARIANT ANNOTATION"
echo "=================="

$annovar_table ${sample_id}.SNPs.PASS.avinput $humandb -buildver hg38 \
-out ${sample_id}.SNPs -remove -protocol refGene,avsnp150 \
-operation g,f -nastring . \
-csvout -polish

$annovar_table ${sample_id}.indels.PASS.avinput $humandb -buildver hg38 \
-out ${sample_id}.indels \
-remove -protocol refGene,avsnp150 \
-operation g,f -nastring . \
-csvout -polish
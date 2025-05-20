job_ids=$(squeue --me -h -o "%A")
for id in $job_ids; do 
	scancel $id
done

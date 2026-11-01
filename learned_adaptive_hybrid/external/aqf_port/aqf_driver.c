/*
用作者的 AdaptiveQF（How-to-Train-Your-Filter 仓库里的 gqf.c，ARM 移植见 src/gqf.c 的“ARM 移植”注释）
跑一条非成员查询流，逻辑照搬 adaptiveqf/src/aqf_adapter.c：先把成员连同反向映射插进去，
每次查询命中都是误报，随即调用 qf_adapt 扩展冲突成员的指纹。

用法：aqf_driver <qbits> <rbits> <members.u64> <queries.u64>
输入文件都是小端 uint64 数组（已哈希的 key）。输出一行 JSON。
*/
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>

#include "include/gqf.h"
#include "include/gqf_int.h"
#include "include/exp_utility.h"

static uint64_t *read_u64(const char *path, size_t *n) {
	FILE *f = fopen(path, "rb");
	if (!f) { perror(path); exit(1); }
	fseek(f, 0, SEEK_END);
	*n = ftell(f) / sizeof(uint64_t);
	fseek(f, 0, SEEK_SET);
	uint64_t *a = malloc(*n * sizeof(uint64_t));
	if (fread(a, sizeof(uint64_t), *n, f) != *n) { perror("fread"); exit(1); }
	fclose(f);
	return a;
}

int main(int argc, char **argv) {
	if (argc != 5) { fprintf(stderr, "usage: %s qbits rbits members.u64 queries.u64\n", argv[0]); return 1; }
	size_t qbits = atoi(argv[1]), rbits = atoi(argv[2]), nm, nq;
	uint64_t *members = read_u64(argv[3], &nm);
	uint64_t *queries = read_u64(argv[4], &nq);

	QF qf;
	if (!qf_malloc(&qf, 1ULL << qbits, qbits + rbits, 0, QF_HASH_INVERTIBLE, 0)) { fprintf(stderr, "qf_malloc\n"); return 1; }
	qf_set_auto_resize(&qf, false);
	set_node *set = calloc(nm, sizeof(set_node));
	struct timeval tc;
	uint64_t ft, st;
	for (size_t i = 0; i < nm; i++) {
		if (!insert_key(&qf, set, nm, members[i], 1, &tc, &ft, &st)) { fprintf(stderr, "insert failed at %zu\n", i); return 1; }
	}
	uint64_t occupied_after_insert = qf_get_num_occupied_slots(&qf);

	uint64_t fp = 0, fp_tail = 0, adapts = 0, tail_from = nq * 8 / 10;
	int full = 0;
	for (size_t i = 0; i < nq; i++) {
		uint64_t idx, hash, orig_key = 0;
		int hash_len;
		if (!qf_query(&qf, queries[i], &idx, &hash, &hash_len, QF_KEY_IS_HASH | QF_NO_LOCK)) continue;
		fp++;
		if (i >= tail_from) fp_tail++;
		if (full) continue;
		uint64_t old_hash = hash;
		set_query(set, nm, hash, &orig_key);
		int len = qf_adapt(&qf, idx, orig_key, queries[i], &hash, QF_KEY_IS_HASH | QF_NO_LOCK);
		if (len > 0) {
			set_delete(set, nm, old_hash);
			set_insert(set, nm, hash, orig_key);
			adapts++;
		} else if (len == QF_NO_SPACE) {
			full = 1;
		}
	}
	printf("{\"qbits\": %zu, \"rbits\": %zu, \"members\": %zu, \"queries\": %zu, \"fp\": %llu, \"fp_tail20\": %llu, "
	       "\"adaptations\": %llu, \"full\": %d, \"size_bytes\": %llu, \"occupied_after_insert\": %llu, "
	       "\"occupied_end\": %llu}\n",
	       qbits, rbits, nm, nq, (unsigned long long)fp, (unsigned long long)fp_tail, (unsigned long long)adapts, full,
	       (unsigned long long)qf_get_total_size_in_bytes(&qf), (unsigned long long)occupied_after_insert,
	       (unsigned long long)qf_get_num_occupied_slots(&qf));
	return 0;
}

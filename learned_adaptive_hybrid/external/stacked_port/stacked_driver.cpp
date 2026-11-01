// 调用 How-to-Train-Your-Filter 仓库里 Deeds 等人原版 StackedFilter（Bloom 层）的驱动，原版代码不改。
// 用法：stacked_driver <total_bits> <positives.u64> <negatives.u64> <cdf.f64> <queries.u64> <out.u8>
// 负例按频率降序，cdf 为累计频率（同 HTTYF 的 build_training_negatives）。输出每个查询 key 是否被接受。
#include <cstddef>
#include <cstdint>
// 只声明要用的 C 接口（stacked_wrapper.h 在 C++ 下会把带函数定义的头文件再引入一遍，导致符号重复）
extern "C" {
struct WrappedStackedFilter;
WrappedStackedFilter *StackedFilterCreate(size_t total_size, const void *positives, size_t num_positives,
                                          const void *negatives, size_t num_negatives, const double *cdf,
                                          size_t cdf_size, double insert_capacity, uint64_t *optimize_ns);
size_t StackedFilterGetSize(WrappedStackedFilter *wrapped_filter);
void StackedFilterDestroy(WrappedStackedFilter *wrapped_filter);
bool StackedFilterLookupElement(WrappedStackedFilter *wrapped_filter, uint64_t *element);
}
#include <cstdio>
#include <cstdlib>
#include <vector>

template <class T> static std::vector<T> load(const char *p) {
    FILE *f = std::fopen(p, "rb");
    if (!f) { std::perror(p); std::exit(1); }
    std::fseek(f, 0, SEEK_END);
    size_t n = std::ftell(f) / sizeof(T);
    std::fseek(f, 0, SEEK_SET);
    std::vector<T> v(n);
    if (n && std::fread(v.data(), sizeof(T), n, f) != n) { std::perror("fread"); std::exit(1); }
    std::fclose(f);
    return v;
}

int main(int argc, char **argv) {
    if (argc != 7) { std::fprintf(stderr, "usage\n"); return 1; }
    size_t total_bits = std::strtoull(argv[1], nullptr, 10);
    auto pos = load<uint64_t>(argv[2]);
    auto neg = load<uint64_t>(argv[3]);
    auto cdf = load<double>(argv[4]);
    auto qry = load<uint64_t>(argv[5]);
    uint64_t opt_ns = 0;
    WrappedStackedFilter *f = StackedFilterCreate(total_bits, pos.data(), pos.size(), neg.data(), neg.size(),
                                                  cdf.data(), cdf.size(), 0, &opt_ns);
    std::vector<uint8_t> out(qry.size());
    for (size_t i = 0; i < qry.size(); i++) out[i] = StackedFilterLookupElement(f, &qry[i]);
    size_t fn = 0;
    for (size_t i = 0; i < pos.size(); i++) fn += !StackedFilterLookupElement(f, &pos[i]);
    FILE *o = std::fopen(argv[6], "wb");
    std::fwrite(out.data(), 1, out.size(), o);
    std::fclose(o);
    std::printf("{\"actual_bits\": %zu, \"false_negatives\": %zu, \"optimize_ms\": %.1f}\n",
                StackedFilterGetSize(f), fn, opt_ns / 1e6);
    StackedFilterDestroy(f);
    return 0;
}

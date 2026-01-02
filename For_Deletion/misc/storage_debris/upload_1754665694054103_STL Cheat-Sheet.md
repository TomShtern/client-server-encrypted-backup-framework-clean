<algorithm>        → sort, find, for_each, copy, remove_if, lower_bound, upper_bound
<array>            → array<T,N>, std::get<>, .size(), .fill()
<bitset>           → bitset<N>, .set(), .reset(), .test(), .count()
<chrono>           → std::chrono::system_clock, std::chrono::steady_clock, duration_cast, milliseconds
<cmath>            → sqrt, pow, sin, cos, abs, log, exp
<complex>          → complex<T>, norm(), real(), imag(), polar()
<condition_variable> → condition_variable, notify_one, wait, notify_all
<deque>            → deque<T>, push_front, push_back, pop_front, pop_back, operator[]
<exception>        → exception, what()
<forward_list>     → forward_list<T>, push_front, before_begin, insert_after
<fstream>          → ifstream, ofstream, fstream, .open(), .close()
<functional>       → function<>, bind, mem_fn, ref, greater<>, less<>
<future>           → future<T>, promise<T>, async, packaged_task<T>
<iomanip>          → setw, setprecision, fixed, scientific, setfill
<ios> / <iosfwd>   → ios_base, ios::sync_with_stdio, forward declarations for streams
<iterator>         → iterator_traits<>, back_inserter, front_inserter, inserter, istream_iterator, ostream_iterator
<list>             → list<T>, push_front, push_back, insert, erase, splice, sort (member)
<map>              → map<Key,T>, insert, find, erase, lower_bound, upper_bound
<memory>           → unique_ptr<T>, shared_ptr<T>, weak_ptr<T>, make_unique, make_shared, allocator<T>
<mutex>            → mutex, lock_guard<>, unique_lock<>, recursive_mutex, try_lock
<new>              → operator new, operator delete, placement new, bad_alloc
<numeric>          → accumulate, inner_product, partial_sum, adjacent_difference, iota, gcd, lcm
<queue>            → queue<T>, push, pop, front, back; priority_queue<T>, top, pop, push
<random>           → mt19937, random_device, uniform_int_distribution, normal_distribution, shuffle
<regex>            → regex, smatch, regex_search, regex_match, regex_replace
<set>              → set<Key>, insert, erase, find, lower_bound, upper_bound, count
<sstream>          → istringstream, ostringstream, stringstream, str(), rdbuf()
<stack>            → stack<T>, push, pop, top, empty
<string>           → string, c_str(), substr, find, find_first_of, append, erase
<thread>           → thread, this_thread::sleep_for, detach, join, hardware_concurrency
<tuple>            → tuple<...>, make_tuple, tie, get<>
<type_traits>      → is_same<>, is_integral<>, enable_if<>, remove_reference<>, decay<>, is_void<>
<unordered_map>    → unordered_map<Key,T>, insert, find, erase, operator[], rehash
<utility>          → pair, make_pair, move, forward, swap, declval
<vector>           → vector<T>, push_back, emplace_back, pop_back, size, at, operator[], begin, end

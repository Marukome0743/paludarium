/* What a veth end without its carrier drops (so as root): tx_dropped of
   /proc/net/dev and of a link's IFLA_STATS64 and IFLA_STATS. A pair, va
   (1000, 10.0.0.1/24) in a network namespace A and vb (1001, 10.0.0.2/24)
   in another, B, both without IPv6; va comes up and vb does not, so va
   never has its carrier, and its queueing discipline stays noop, which
   drops each packet it is to send (noop_enqueue): the ARP request for a
   datagram to vb, whose datagram waits for an answer; a broadcast, and of
   one in fragments the first, as the drop stops the rest
   (ip_do_fragment); and a datagram to a group. vb takes nothing in.
   The case reads the counters at once, before ARP asks again (1 s). */
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <poll.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define NLM_F_REQUEST 1
#define NLM_F_ACK 4
#define NLM_F_DUMP 0x300
#define NLM_F_CREATE 0x400
#define NLMSG_ERROR 2
#define NLMSG_DONE 3
#define RTM_NEWLINK 16
#define RTM_GETLINK 18
#define RTM_NEWADDR 20
#define IFLA_IFNAME 3
#define IFLA_STATS 7
#define IFLA_LINKINFO 18
#define IFLA_STATS64 23
#define IFLA_NET_NS_FD 28
#define IFLA_INFO_KIND 1
#define IFLA_INFO_DATA 2
#define VETH_INFO_PEER 1
#define IFA_LOCAL 2
#define IFA_ADDRESS 1
#define VA 1000
#define VB 1001

struct body {
    unsigned char bytes[512];
    size_t len;
};
static unsigned seq;

static long result(long r) { return r < 0 ? -errno : r; }
static void raw(struct body *b, const void *value, size_t len) {
    memcpy(b->bytes + b->len, value, len);
    b->len += (len + 3) & ~3u;
}
static void put(struct body *b, unsigned short type, const void *value, size_t len) {
    unsigned short attribute[2] = {(unsigned short)(4 + len), type};
    memcpy(b->bytes + b->len, attribute, 4);
    memcpy(b->bytes + b->len + 4, value, len);
    b->len += (4 + len + 3) & ~3u;
}
static size_t begin(struct body *b, unsigned short type) {
    size_t at = b->len;
    put(b, type, NULL, 0);
    return at;
}
static void end(struct body *b, size_t at) {
    unsigned short len = (unsigned short)(b->len - at);
    memcpy(b->bytes + at, &len, 2);
}
/* Sends a request on `fd` and prints its acknowledgement's error. */
static void request(int fd, unsigned short type, const struct body *b, const char *label) {
    unsigned char buf[4096] = {0};
    const unsigned head[4] = {(unsigned)(16 + b->len), type | (NLM_F_REQUEST | NLM_F_ACK | NLM_F_CREATE) << 16, ++seq, 0};
    memcpy(buf, head, 16);
    memcpy(buf + 16, b->bytes, b->len);
    send(fd, buf, head[0], 0);
    struct pollfd ready = {.fd = fd, .events = POLLIN};
    if (poll(&ready, 1, 2000) <= 0 || recv(fd, buf, sizeof buf, 0) < 20) {
        printf("%s: no answer\n", label);
        return;
    }
    int error;
    memcpy(&error, buf + 16, 4);
    printf("%s: error=%d\n", label, error);
}
static void up(int fd, int index, const char *label) {
    struct body b = {0};
    const unsigned m[4] = {0, (unsigned)index, IFF_UP, IFF_UP};
    raw(&b, m, 16);
    request(fd, RTM_NEWLINK, &b, label);
}
static void address(int fd, int index, const char *ip, const char *label) {
    struct body b = {0};
    const unsigned char m[8] = {AF_INET, 24, 0, 0, (unsigned char)index, (unsigned char)(index >> 8), 0, 0};
    unsigned char in[4];
    inet_pton(AF_INET, ip, in);
    raw(&b, m, 8);
    put(&b, IFA_LOCAL, in, 4);
    put(&b, IFA_ADDRESS, in, 4);
    request(fd, RTM_NEWADDR, &b, label);
}
static void write_file(const char *path, const char *text) {
    int fd = open(path, O_WRONLY);
    long n = fd < 0 ? -errno : result(write(fd, text, strlen(text)));
    if (fd >= 0) close(fd);
    printf("%s <- %s: %ld\n", path, text, n);
}

/* The lines of lo, va and vb in /proc/net/dev of the namespace the
   process is in, and each link's IFLA_STATS64 and IFLA_STATS, their first
   eight fields (packets, bytes, errors and drops), as the dump of `fd`
   gives them. */
static void counters(int fd, const char *label) {
    printf("-- %s\n", label);
    char text[8192];
    int f = open("/proc/net/dev", O_RDONLY);
    long n = f < 0 ? 0 : read(f, text, sizeof text - 1);
    if (f >= 0) close(f);
    text[n > 0 ? n : 0] = 0;
    for (char *line = text, *next; *line; line = next) {
        next = strchr(line, '\n');
        if (!next) break;
        *next++ = 0;
        if (strstr(line, " lo:") || strstr(line, " va:") || strstr(line, " vb:")) printf("%s\n", line);
    }
    unsigned char buf[16384];
    const unsigned char m[16] = {AF_UNSPEC};
    unsigned head[4] = {32, RTM_GETLINK | (NLM_F_REQUEST | NLM_F_DUMP) << 16, ++seq, 0};
    memcpy(buf, head, 16);
    memcpy(buf + 16, m, 16);
    send(fd, buf, 32, 0);
    for (;;) {
        struct pollfd ready = {.fd = fd, .events = POLLIN};
        if (poll(&ready, 1, 2000) <= 0) {
            printf("no end\n");
            return;
        }
        long got = recv(fd, buf, sizeof buf, 0);
        for (long at = 0; at + 16 <= got;) {
            unsigned len;
            unsigned short kind;
            memcpy(&len, buf + at, 4);
            memcpy(&kind, buf + at + 4, 2);
            if (len < 16 || at + len > got) break;
            if (kind == NLMSG_DONE || kind == NLMSG_ERROR) return;
            const unsigned char *msg = buf + at;
            char name[16] = "?";
            unsigned long long wide[8] = {0};
            unsigned narrow[8] = {0};
            for (unsigned a = 32; a + 4 <= len;) {
                unsigned short alen, type;
                memcpy(&alen, msg + a, 2);
                memcpy(&type, msg + a + 2, 2);
                if (alen < 4) break;
                if (type == IFLA_IFNAME) snprintf(name, sizeof name, "%s", (const char *)msg + a + 4);
                if (type == IFLA_STATS64 && alen >= 4 + 64) memcpy(wide, msg + a + 4, 64);
                if (type == IFLA_STATS && alen >= 4 + 32) memcpy(narrow, msg + a + 4, 32);
                a += (alen + 3) & ~3u;
            }
            at += (len + 3) & ~3u;
            if (strcmp(name, "lo") && strcmp(name, "va") && strcmp(name, "vb")) continue;
            printf("%s stats64", name);
            for (int i = 0; i < 8; i++) printf(" %llu", wide[i]);
            printf(" stats");
            for (int i = 0; i < 8; i++) printf(" %u", narrow[i]);
            printf("\n");
        }
    }
}

/* `fd` sends `len` bytes to `ip` port `port`; then, if `wait` is a socket,
   whether that takes a datagram within 2 s, which it drains. */
static void udp(int fd, int family, const char *ip, int port, size_t len, int wait, const char *label) {
    static char data[70000];
    memset(data, 'x', sizeof data);
    struct sockaddr_storage to = {0};
    socklen_t size;
    if (family == AF_INET) {
        struct sockaddr_in *a = (void *)&to;
        a->sin_family = AF_INET;
        a->sin_port = htons((unsigned short)port);
        inet_pton(AF_INET, ip, &a->sin_addr);
        size = sizeof *a;
    } else {
        struct sockaddr_in6 *a = (void *)&to;
        a->sin6_family = AF_INET6;
        a->sin6_port = htons((unsigned short)port);
        inet_pton(AF_INET6, ip, &a->sin6_addr);
        size = sizeof *a;
    }
    printf("%s: %ld", label, result(sendto(fd, data, len, 0, (void *)&to, size)));
    if (wait >= 0) {
        struct pollfd ready = {.fd = wait, .events = POLLIN};
        int got = poll(&ready, 1, 2000);
        printf(" taken=%d", got);
        if (got > 0) recv(wait, data, sizeof data, 0);
    }
    printf("\n");
}
static int route_socket(void) { return socket(AF_NETLINK, SOCK_RAW, 0); }
int main(int argc, char **argv) {
    if (argc < 2 || strcmp(argv[1], "net-dev-dropped")) return 99;
    setvbuf(stdout, NULL, _IOLBF, 0);
    printf("unshare=%ld\n", result(unshare(CLONE_NEWNET)));
    int ns_a = open("/proc/self/ns/net", O_RDONLY);
    int ctl = route_socket();
    write_file("/proc/sys/net/ipv6/conf/all/disable_ipv6", "1");
    write_file("/proc/sys/net/ipv6/conf/default/disable_ipv6", "1");
    up(ctl, 1, "lo up");
    printf("unshare=%ld\n", result(unshare(CLONE_NEWNET)));
    int ns_b = open("/proc/self/ns/net", O_RDONLY);
    int far = route_socket();
    write_file("/proc/sys/net/ipv6/conf/all/disable_ipv6", "1");
    write_file("/proc/sys/net/ipv6/conf/default/disable_ipv6", "1");
    printf("setns=%ld\n", result(setns(ns_a, CLONE_NEWNET)));
    struct body m = {0};
    const unsigned a[4] = {0, VA, 0, 0}, b[4] = {0, VB, 0, 0};
    raw(&m, a, 16);
    put(&m, IFLA_IFNAME, "va", 3);
    size_t link = begin(&m, IFLA_LINKINFO);
    put(&m, IFLA_INFO_KIND, "veth", 5);
    size_t data = begin(&m, IFLA_INFO_DATA), peer = begin(&m, VETH_INFO_PEER);
    raw(&m, b, 16);
    put(&m, IFLA_IFNAME, "vb", 3);
    put(&m, IFLA_NET_NS_FD, &ns_b, 4);
    end(&m, peer);
    end(&m, data);
    end(&m, link);
    request(ctl, RTM_NEWLINK, &m, "make va, and vb in B");
    address(ctl, VA, "10.0.0.1", "va's 10.0.0.1/24");
    address(far, VB, "10.0.0.2", "vb's 10.0.0.2/24");
    up(ctl, VA, "va up, vb down");
    counters(ctl, "A, va without its carrier");

    int s = socket(AF_INET, SOCK_DGRAM, 0), one = 1;
    setsockopt(s, SOL_SOCKET, SO_BROADCAST, &one, sizeof one);
    udp(s, AF_INET, "10.0.0.2", 7000, 10, -1, "10 bytes to vb");
    udp(s, AF_INET, "10.0.0.255", 7000, 10, -1, "a broadcast of 10 bytes");
    udp(s, AF_INET, "10.0.0.255", 7000, 3000, -1, "a broadcast of 3000 bytes, in fragments");
    struct ip_mreqn out = {.imr_ifindex = VA};
    setsockopt(s, IPPROTO_IP, IP_MULTICAST_IF, &out, sizeof out);
    udp(s, AF_INET, "239.1.2.3", 7000, 10, -1, "10 bytes to 239.1.2.3");
    counters(ctl, "A, each dropped");
    printf("setns=%ld\n", result(setns(ns_b, CLONE_NEWNET)));
    counters(far, "B, nothing taken in");
    return 0;
}

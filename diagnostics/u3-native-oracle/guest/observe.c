/* Native-only oracle: every invocation computes fresh expectations. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <cpuid.h>
struct u3_case { const char *name; void (*run)(void *, const void *); const unsigned char *op, *end; };
#include "cases.h"
static void hex(const unsigned char *p,size_t n) { for(size_t i=0;i<n;i++) printf("%02x",p[i]); }
int main(void) {
    unsigned int a,b,c,d;
    __cpuid_count(1,0,a,b,c,d);
    if(!(c&(1u<<25)) || !(c&(1u<<1))) { fputs("native AES/PCLMUL unavailable\n",stderr); return 2; }
    __cpuid_count(7,0,a,b,c,d);
    if(!(b&(1u<<29))) { fputs("native SHA unavailable\n",stderr); return 2; }
    for(size_t i=0;i<sizeof(cases)/sizeof(cases[0]);i++) {
        for(unsigned pattern=0;pattern<8;pattern++) for(unsigned mode=0;mode<4;mode++) {
            unsigned char input[512],output[280];
            for(unsigned k=0;k<sizeof(input);k++) input[k]=(unsigned char)(pattern==0?0:pattern==1?k*17+3:pattern==2?255:k*31+pattern*47);
            static const uint64_t special[]={0,0x8000000000000000ULL,0x7ff0000000000000ULL,0x7ff8000000000042ULL,1,0x0010000000000000ULL,0x3ff0000000000000ULL,0x7fefffffffffffffULL};
            if(pattern>=3) for(unsigned k=0;k<32;k++) memcpy(input+k*8,&special[(k+pattern)%8],8);
            uint32_t mxcsr=0x1f80u|(mode<<13); memcpy(input+256,&mxcsr,4);
            memset(output,0,sizeof(output)); cases[i].run(output,input);
            printf("%s|%u|%u|",cases[i].name,pattern,mode);
            hex(cases[i].op,(size_t)(cases[i].end-cases[i].op)); putchar('|');
            hex(input,sizeof(input)); putchar('|'); hex(output,sizeof(output)); putchar('|'); hex(input,sizeof(input)); putchar('\n');
        }
    }
    return ferror(stdout)?3:0;
}

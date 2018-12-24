// Practicing bit manipulation
#include <cstdint>
#include <cassert>
#include <cstring>
#include <stdexcept>
#include <iostream>
#include <bitset>

#define DEBUG 1

void debug_u32(std::string name, uint32_t value)
{
#if DEBUG
    std::cout << name << ": " << std::bitset<32>(value) << std::endl;
#endif
}

/*!
    \param N First input integer
    \param M Second input integer
    \param i Starting bit position
    \param j Ending bit position 
    \return N with all bits between i and j set to the lower bits of M
 */
uint32_t merge_integers(uint32_t N, uint32_t M, uint32_t i, uint32_t j)
{
    if(j < i)
    {
        throw std::invalid_argument("j shall be greater than or equal to i");
    }

    // Mask to copy from M
    uint32_t src_selection = (1UL << ((j-i)+1)) - 1UL;
    // Mask to apply to N
    uint32_t dest_selection = (1UL << (j+1)) - 1UL;
    if(i > 0)
    {
        uint32_t lower_bits = (1UL << (i)) - 1UL;
        dest_selection ^= lower_bits;
    }

    // Get and shift part to apply
    uint32_t part_of_M = M & src_selection;
    uint32_t part_of_M_shifted = part_of_M;
    if(i > 0)
    {
        part_of_M_shifted <<= i;
    }

    // Add bits
    N |= part_of_M_shifted;

    // Remove additional bits
    uint32_t to_remove = N & ~part_of_M_shifted & dest_selection;
    N ^= to_remove;
    return N;
}

/*!
    \param float_str Float passed as string
    \return The binary representation of the float as string
 */
std::string float_to_binary_string(std::string float_str)
{
    float float_value = std::stof(float_str);
    char buf[4];
    memcpy(buf, &float_value, 4);
    uint32_t uint_value = (uint32_t)buf[3] << 24 | (uint32_t)buf[2] << 16 | (uint32_t)buf[1] << 8 | (uint32_t)buf[0];

    char output_buffer[33];
    output_buffer[32] = 0;
    for(int i=0; i < 32; i++)
    {
        int char_index = 31-i;
        if(uint_value & (1U<<i))
        {
            output_buffer[char_index] = '1';
        }
        else
        {
            output_buffer[char_index] = '0';
        }
    }

    return std::string(output_buffer);
}

int main(void)
{
    try
    {
        uint32_t merged1 = merge_integers(0b10000000000, 0b10101, 2, 6);
        assert(merged1 == 0b10001010100);
        std::cout << ".";

        uint32_t merged2 = merge_integers(0b10000000000, 0b10101, 0, 2);
        assert(merged2 == 0b10000000101);
        std::cout << ".";

        uint32_t merged3 = merge_integers(0b10000011111, 0b10101, 2, 6);
        assert(merged3 == 0b10001010111);
        std::cout << ".";

        std::string binary_str1 = float_to_binary_string("3.72");
        assert(binary_str1 == "01000000011011100001010001111011");
        std::cout << ".";

        std::string binary_str2 = float_to_binary_string("2.25125");
        assert(binary_str2 == "01000000000100000001010001111011");
        std::cout << ".";
        
        std::cout << "\nOK\n";
    }
    catch (std::exception & e)
    {
        std::cerr << "ERROR: " << e.what();
    }
}


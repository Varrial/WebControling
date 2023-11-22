text = "0🌘01mayshellXXXVearthxbcbxaustraliaRg1+🐔Al 🏋️‍♂️🏋️‍♂️🏋️‍♂️I am lovedhttps://youtu.be/phA_mGxR4-A#40cb1a🐛🐛🐛🐛🐛02:400107"
suma = 0
for letter in text:
    try:
        a = int(letter)
        print('\t', a)
        suma += a
    except:
        pass

print(suma)
### 使用云打码识别图片验证码
def getCode(image_name):
    ### 打码自己解决 ！！！
    print('------正在使用云打码识别验证码------\n')
    print('调用云打码接口失败，请手动打开'+image_name)
    answer_num = input('输入符合要求的验证图片的下标，比如 23 ：\n')
    print('你输入的数字为'+image_name)
    return answer_num
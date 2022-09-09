import raw_image_show as rawshow
import numpy as np
import math

def read_packed_word(file_path_name, height, width, bayer):
    # 当行长度补齐
    new_width=int(math.floor((width+3)/4)*4)#对四字节补齐
    packet_num_L = new_width // 4
    width_byte_num=packet_num_L*5#当行byte长度
    width_byte_num=int(math.floor((width_byte_num+79)/80)*80)#当行对8字节补齐
    new_width=int(width_byte_num / 5 * 4)
    # 求对应的商和余值
    packet_num_L, Align_num = divmod(width_byte_num, 5)
    image_bytes=width_byte_num*height
    frame=np.fromfile(file_path_name,count=image_bytes,dtype="uint8")
    print("bshape",frame.shape)
    print('%#x'%frame[0])
    frame.shape=[height,width_byte_num]#高字节整理图像矩阵
    one_byte=frame[:,0:image_bytes:5]
    two_byte=frame[:,1:image_bytes:5]
    three_byte=frame[:,2:image_bytes:5]
    four_byte=frame[:,3:image_bytes:5]
    five_byte=frame[:,4:image_bytes:5]
    if Align_num==1:
        two_byte=np.column_stack((two_byte,np.arange(1,height+1)))
        three_byte=np.column_stack((three_byte,np.arange(1,height+1)))
        four_byte=np.column_stack((four_byte,np.arange(1,height+1)))
        five_byte=np.column_stack((five_byte,np.arange(1,height+1)))
        print('Aligh is 1')
    elif Align_num==2:
        three_byte=np.column_stack((three_byte,np.arange(1,height+1)))
        four_byte=np.column_stack((four_byte,np.arange(1,height+1)))
        five_byte=np.column_stack((five_byte,np.arange(1,height+1)))
        print('Aligh is 2')
    elif Align_num==3:
        four_byte=np.column_stack((four_byte,np.arange(1,height+1)))
        five_byte=np.column_stack((five_byte,np.arange(1,height+1)))
        print('Aligh is 3')
    elif Align_num==4:
        five_byte=np.column_stack((five_byte,np.arange(1,height+1)))
        print('Aligh is 4')
    else:
        print('That is not to Aligh')
#数据转换防止溢出
    one_byte=one_byte.astype('uint16')
    two_byte=two_byte.astype('uint16')
    three_byte=three_byte.astype('uint16')
    four_byte=four_byte.astype('uint16')
    five_byte=five_byte.astype('uint16')
#用矩阵的方法进行像素的拼接
    one_byte=np.left_shift(np.bitwise_and((two_byte),3),10) + np.left_shift(one_byte,2)
    two_byte=np.bitwise_and((two_byte),252)+np.left_shift(np.bitwise_and((three_byte),15),8)
    three_byte=np.right_shift(np.bitwise_and((three_byte),240),2)+np.left_shift(np.bitwise_and((four_byte),63),6)
    four_byte=np.right_shift(np.bitwise_and((four_byte),192),4)+np.left_shift(five_byte,4)

    frame_pixels=np.zeros(shape=(height,new_width))
    frame_pixels[:,0:new_width:4]=one_byte[:,0:packet_num_L]
    frame_pixels[:,1:new_width:4]=two_byte[:,0:packet_num_L]
    frame_pixels[:,2:new_width:4]=three_byte[:,0:packet_num_L]
    frame_pixels[:,3:new_width:4]=four_byte[:,0:packet_num_L]
# 裁剪无用的数据
    frame_out=frame_pixels[:,0:width]
    
    raw_name=file_path_name[:-12]
    raw_name=raw_name.replace('_10_','_12_')
    raw_byte=frame_out
    frame_raw_low=np.uint8(raw_byte)
    raw_byte=raw_byte.astype('uint16')
    raw_byte=np.right_shift(raw_byte,8)
    frame_raw_high=raw_byte
    raw_width=width*2
    frame_raw=np.zeros(shape=(height,raw_width))
    frame_raw[:,0:raw_width:2]=frame_raw_low
    frame_raw[:,1:raw_width:2]=frame_raw_high
    frame_raw=frame_raw.astype('uint8')
    frame_raw.tofile(raw_name+".raw")
    # 根据bayer转换raw
    rgb_img=np.zeros(shape=(height,width,3))
    R=rgb_img[:,:,0]
    GR=rgb_img[:,:,1]
    GB=rgb_img[:,:,1]
    B=rgb_img[:,:,2]
    # 0:B 1:GB 2:GR 3:R
    if (bayer==3):
        R[::2,::2]=frame_out[::2,::2]
        GR[::2,1::2]=frame_out[::2,1::2]
        GB[1::2,::2]=frame_out[1::2,::2]
        B[1::2,1::2]=frame_out[1::2,1::2]
    elif (bayer==2):
        GR[::2,::2]=frame_out[::2,::2]
        R[::2,1::2]=frame_out[::2,1::2]
        B[1::2,::2]=frame_out[1::2,::2]
        GB[1::2,1::2]=frame_out[1::2,1::2]
    elif (bayer==1):
        GB[::2,::2]=frame_out[::2,::2]
        B[::2,1::2]=frame_out[::2,1::2]
        R[1::2,::2]=frame_out[1::2,::2]
        GR[1::2,1::2]=frame_out[1::2,1::2]
    elif (bayer==0):
        B[::2,::2]=frame_out[::2,::2]
        GB[::2,1::2]=frame_out[::2,1::2]
        GR[1::2,::2]=frame_out[1::2,::2]
        R[1::2,1::2]=frame_out[1::2,1::2]
    else:
        print("no match bayer")
        return
    return  rgb_img

def test_case_read_packed_word():
    #file_name="image\Input_4032_3024_RGGB.raw"
 #   file_name="CWF-MCC.raw"
    file_name="101907391-0060-0060-main-P1-IMGO-PW4672-PH2612-BW5840__4640x2612_10_2.packed_word"
#    image=read_mipi10_file(file_name,1728,2304)
    image=read_packed_word(file_name,2612,4640)
    #image=read_mipi10_file(file_name,3024,4032)
    #image=image/255.0
    image=image/4095.0

    rawshow.raw_image_show_thumbnail(image,2612,4640)
#    rawshow.raw_image_show_thumbnail(image,1728,2304)
    #rawshow.raw_image_show_fullsize(image,3024,4032)
    #rawshow.raw_image_show_3D(image,3024,4032)
    #rawshow.raw_image_show_fakecolor(image,3024,4032,"RGGB")
#    rawshow.raw_image_show_fakecolor(image,1728,2304,"GRBG")



if __name__=="__main__":
    print('This is main of module')
    x=test_case_read_packed_word()
    print(x)

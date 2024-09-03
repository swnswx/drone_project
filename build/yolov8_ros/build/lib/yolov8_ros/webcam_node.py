import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class WebcamNode(Node):

    def __init__(self):
        super().__init__('webcam_node')
        
        # /camera/rgb/image_raw 토픽 발행
        self.publisher_ = self.create_publisher(Image, '/camera/rgb/image_raw', 10)
        
        # dbg_image 토픽 구독
        self.subscription = self.create_subscription(
            Image,
            '/yolo/dbg_image',  # DebugNode에서 발행된 토픽
            self.listener_callback,
            10)
        
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10Hz로 이미지를 발행
        #self.cap = cv2.VideoCapture(0)  # 기본 웹캠 장치를 엽니다 (0은 첫 번째 장치)
        self.cap = cv2.VideoCapture(r'/home/sw/detection_ws/src/yolov8_ros/include/안전벨트착용.mp4')  # 동영상 파일을 엽니다
        self.bridge = CvBridge()

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().error('Failed to capture image')
            return

        # 프레임 크기를 640x640으로 조정
        frame_resized = cv2.resize(frame, (640, 640))
        
        # 이미지를 sensor_msgs/Image 메시지로 변환하여 발행
        msg = self.bridge.cv2_to_imgmsg(frame_resized, encoding="bgr8")
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing image')

    def listener_callback(self, msg):
        self.get_logger().info("Received dbg_image message")
        # dbg_image 토픽으로부터 ROS 이미지 메시지를 수신
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        # OpenCV 창에 이미지를 표시
        cv2.imshow("Webcam with Bounding Boxes", cv_image)
        
        # OpenCV 창이 반응하도록 대기
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' 키를 누르면 종료
            rclpy.shutdown()

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()  # OpenCV 창을 닫습니다
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = WebcamNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

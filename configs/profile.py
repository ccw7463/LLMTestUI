from . import *

@dataclass
class GetProfile():
    profiles: Dict[str, Dict[str, str]] = field(
        default_factory=lambda: {
            "ChatBot": {
                "name": "LLMTestUI",
                "markdown_description": "LLMTestUI",
                "icon": "https://i.postimg.cc/P5RnGyXD/logo-blank.png",
            }
        }
    )
    
    def get_cl_chat_profiles(self):
        return [
            {
                "name": profile["name"],
                "markdown_description": profile["markdown_description"],
                "icon": profile["icon"],
                "starters": starter_set
            }
            for profile in GetProfile().profiles.values()
        ]

starter_set = [
    cl.Starter(
        label="보고서 작성",
        message="""2차전지 최신 동향에 대한 보고서를 작성해주세요.""",
        icon="https://i.postimg.cc/sDBFR8XJ/simple-report-icon.png"),
    cl.Starter(
        label="번역",
        message="""다음 내용을 영어로 번역해주세요. \n이차전지란 쉽게 말해 한번 사용한 후에도 충전을 통해 재사용이 가능한 전지를 말한다. 이차전지는 양극과 음극, 전해질과 분리막으로 구성되는데, 여기에 이온이 양극과 음극을 오가며 전기 에너지를 발생시키는 원리로 작동한다. 방전할 때는 이온이 음극에서 양극으로, 충전할 때는 양극에서 음극으로 이동하며 에너지를 저장하고 방출하는 것이다.""",
        icon="https://i.postimg.cc/CxDWRqbB/simple-translation-logo.png"),
    cl.Starter(
        label="아이디어",
        message="""2차전지를 홍보하기 위한 전략에는 어떤게 있을까요?""",
        icon="https://i.postimg.cc/wBpnLjkW/simple-lamp-icon.png")
]
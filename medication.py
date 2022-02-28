import json
from flask import Flask, request
app = Flask(__name__)

with open('/home/PlT/drk/medication.json') as json_file:
    medication_Dict = json.load(json_file)

@app.route('/')
def hello_world():
    return "Hello world!"


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    query_result = req.get('queryResult')
    if query_result.get('action') == "analyze-3-symptom":
        sym1 = query_result.get('parameters').get('sym_1')
        sym2 = query_result.get('parameters').get('sym_2')
        sym3 = query_result.get('parameters').get('sym_3')
        print(sym1, sym2, sym3)
        return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
            {
                "text": {"text": [
                "อาการของคุณมีดังต่อไปนี้\n- " + sym1 + "\n- " + sym2 +"\n- " + sym3
                ]
                },
                "platform": "LINE"
            },
            {
                "quickReplies": {
                "title": "ใช่หรือไม่",
                "quickReplies": ["ใช่", "ไม่"]
            },
                "platform": "LINE"
            }]
        }
    elif query_result.get('action') == "all-symptom":
        temp = "โรคภายในระบบมีทั้งหมด "+str(len(medication_Dict))+" โรค ดังนี้\n"
        for i in range(0, len(medication_Dict), 1):
            temp += str(medication_Dict[i]["ID"])+" | "+medication_Dict[i]["Name"]+"\n"
        return {
        "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
            {
                "text": {"text": [temp]
                },
                "platform": "LINE"
            }
            ]
        }
    elif query_result.get('action') == "analyze-3-symptom-yn":
        if query_result.get('queryText') == "ใช่":
          sym1 = query_result.get('outputContexts')[0].get('parameters').get('sym_1')
          sym2 = query_result.get('outputContexts')[0].get('parameters').get('sym_2')
          sym3 = query_result.get('outputContexts')[0].get('parameters').get('sym_3')

          if sym1 == sym2 or sym1 == sym3 or sym2 == sym3:
            return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
            {
                "text": {"text": [
                "อาการที่ถูกเลือกมา มีข้อมูลซ้ำ"
                ]
                },
                "platform": "LINE"
            },
            {
                "text": {"text": [
                'โปรดเริ่มต้นการวิเคราะห์อาการใหม่ ด้วยการกดที่ปุ่ม "เริ่มวิเคราะห์อาการ"'
                ]
                },
                "platform": "LINE"
            }]
            }

          print(sym1, sym2, sym3)

          symptom_result = set()
          check = 0
          for i in medication_Dict:
            for j in i["Start_Symptom"]:
              if j == sym1:
                check += 1
              if j == sym2:
                check += 1
              if j == sym3:
                check += 1
            if check >= 2:
              symptom_result.add(i["ID"])
            check = 0

          print(symptom_result)
          temp = '{"c":['
          for i in symptom_result:
            temp += str(i)+",0,0,"
          temp += "0,0,"

          all = 0
          for i in symptom_result:
            all += int(len(medication_Dict[i-1]["Long_Symptom"]))
          temp += str(all)+"]}"

          if(len(symptom_result) == 0):
            temp = "set()"

          print(temp)
          return {
              "displayText": '25',
              "source": "webhookdata",
              "outputContexts" : [
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/code_analyze",
                  "lifespanCount" : 1,
                  "parameters" : {
                    "code" : temp
                  }
                }
              ],
              "fulfillmentMessages": [
              {
                "payload": {
                  "line": {
                  "altText": "Imagemap From Dr.K",
                  "baseSize": {
                    "height": 1040,
                    "width": 1040
                  },
                "baseUrl": "https://i.ibb.co/Y7K5VSV/a.jpg",
                "type": "imagemap",
                "actions": []
                  }
              },
                "platform": "LINE"
              },
              {
                  "text": {
                    "text": [temp]
                  },
                  "platform": "LINE"
              },
              {
                  "text": {
                    "text": [
                  "ถ้ารหัสวินิจฉัยโรคของคุณคือ set() หมายความว่าข้อมูลของเรายังไม่เพียงพอที่จะตอบอาการดังกล่าวในขณะนี้ คุณสามารถลองวินิจฉัยอาการอีกครั้ง ด้วยอาการอื่นๆ ได้หากต้องการ"
                  ]
                  },
                  "platform": "LINE"
              }
              ]
          }
        else :
          return {
            "displayText": '25',
            "source": "webhookdata",
            "fulfillmentMessages": [
            {
                "text": {"text": [
                'โปรดเริ่มต้นการวิเคราะห์อาการใหม่ ด้วยการกดที่ปุ่ม "เริ่มวิเคราะห์อาการ"'
                ]
                },
                "platform": "LINE"
            }]
          }
    elif query_result.get('action') == "code-output":
        code = query_result.get('queryText')
        x = json.loads(code)
        x["c"][1] = x["c"][1]-1
        x["c"][2] = x["c"][2]-1
        print(x)
        code_rewrite = ""
        for i in str(x):
          if i == " ":
            continue
          elif i == "\'":
            code_rewrite += "\""
          else:
            code_rewrite += i
        return {
              "displayText": '25',
              "source": "webhookdata",
              "outputContexts" : [
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/analyze_starter",
                  "lifespanCount" : int(x["c"][len(x["c"])-1]),
                  "parameters" : {
                    "code" : code_rewrite
                  }
                }
              ],
              "fulfillmentMessages": [
              {
                  "text": {
                    "text": [
                  "ยืนยันการวินิจฉัยโรคทั้งหมด "+str(x["c"][len(x["c"])-1])+" คำถาม"
                  ]
                  },
                  "platform": "LINE"
              },
              {
                  "text": {
                    "text": [
                  "(บริการของเราไม่ใช่คำวินิจฉัยของแพทย์ แต่เป็นเพียงการให้ข้อมูลเบื้องต้นเท่านั้น หากมีข้อสงสัย ควรปรึกษาแพทย์ผู้เชี่ยวชาญเพิ่มเติม)"
                  ]
                  },
                  "platform": "LINE"
              },
              {
                "quickReplies": {
                "title": "ยืนยันการวินิจฉัยโรค",
                "quickReplies": ["ใช่"]
              },
                "platform": "LINE"
              }
              ]
          }
    elif query_result.get('action') == "analyzing":
        code = query_result.get('outputContexts')[0].get('parameters').get('code')
        x = json.loads(code)
        print(x)
        if query_result.get('queryText') == "ใช่":
          if  x["c"][len(x["c"])-1] == x["c"][len(x["c"])-2]:
              x["c"][1+x["c"][len(x["c"])-3]] = x["c"][1+x["c"][len(x["c"])-3]]+1
              temp = "โรคที่อาจเกิดขึ้นมีดังนี้\n\n"
              for i in range(0, (len(x["c"]))-3, 3):
                temp += str(x["c"][i+1])+"/"+str(len(medication_Dict[x["c"][i]-1]["Long_Symptom"]))+" | "+medication_Dict[x["c"][i]-1]["Name"]+"\n"
              print(x)
              return {
              "displayText": '25',
              "source": "webhookdata",
              "fulfillmentMessages": [
              {
                  "text": {
                    "text": [temp]
                  },
                  "platform": "LINE"
              }
              ]
              }
          elif x["c"][2+x["c"][len(x["c"])-3]] == len(medication_Dict[x["c"][x["c"][len(x["c"])-3]]-1]["Long_Symptom"])-1:
                x["c"][1+x["c"][len(x["c"])-3]] = x["c"][1+x["c"][len(x["c"])-3]]+1
                x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]+1
                x["c"][len(x["c"])-3] = x["c"][len(x["c"])-3]+3
                x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]-1
                x["c"][1+x["c"][len(x["c"])-3]] = x["c"][1+x["c"][len(x["c"])-3]]-1
          x["c"][len(x["c"])-2] = x["c"][len(x["c"])-2]+1
          x["c"][1+x["c"][len(x["c"])-3]] = x["c"][1+x["c"][len(x["c"])-3]]+1
          x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]+1

        elif query_result.get('queryText') == "ไม่":
          if  x["c"][len(x["c"])-1] == x["c"][len(x["c"])-2]:
            temp = ""
            for i in range(0, (len(x["c"]))-3, 3):
              temp += str(x["c"][i+1])+"/"+str(len(medication_Dict[x["c"][i]-1]["Long_Symptom"]))+" | "+medication_Dict[x["c"][i]-1]["Name"]+"\n"
            print(x)
            return {
              "displayText": '25',
              "source": "webhookdata",
              "fulfillmentMessages": [
              {
                  "text": {
                    "text": [temp]
                  },
                  "platform": "LINE"
              }
              ]
              }
          elif x["c"][2+x["c"][len(x["c"])-3]] == len(medication_Dict[x["c"][x["c"][len(x["c"])-3]]-1]["Long_Symptom"])-1:
                x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]+1
                x["c"][len(x["c"])-3] = x["c"][len(x["c"])-3]+3
                x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]-1
          x["c"][len(x["c"])-2] = x["c"][len(x["c"])-2]+1
          x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]+1
        symptom = x["c"][x["c"][len(x["c"])-3]]-1
        question = x["c"][2+x["c"][len(x["c"])-3]]
        q = medication_Dict[symptom]["Long_Symptom"][question]
        temp = str(x["c"][len(x["c"])-2])+"/"+str(x["c"][len(x["c"])-1])+" | "+q
        code_rewrite = ""
        for i in str(x):
          if i == " ":
            continue
          elif i == "\'":
            code_rewrite += "\""
          else:
            code_rewrite += i
        print(code_rewrite)
        return {
              "displayText": '25',
              "source": "webhookdata",
              "outputContexts" : [
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/analyze_starter",
                  "lifespanCount" : (int(x["c"][len(x["c"])-1])-int(x["c"][len(x["c"])-2]))+1,
                  "parameters" : {
                    "code" : code_rewrite
                  }
                }
              ],
              "fulfillmentMessages": [
              {
                  "text": {
                    "text": [temp]
                  },
                  "platform": "LINE"
              },
              {
                "quickReplies": {
                "title": "ใช่หรือไม่",
                "quickReplies": ["ใช่", "ไม่"]
              },
                "platform": "LINE"
              }
              ]
          }
    elif query_result.get('action') == "covid-starter":
        code = '{"c":[57,0,0,0,0,11]}'
        x = json.loads(code)
        x["c"][1] = x["c"][1]-3
        x["c"][2] = x["c"][2]-1
        print(x)
        code_rewrite = ""
        for i in str(x):
          if i == " ":
            continue
          elif i == "\'":
            code_rewrite += "\""
          else:
            code_rewrite += i
        return {
              "displayText": '25',
              "source": "webhookdata",
              "outputContexts" : [
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/covid_starter",
                  "lifespanCount" : int(x["c"][len(x["c"])-1]),
                  "parameters" : {
                    "code" : code_rewrite
                  }
                }
              ],
              "fulfillmentMessages": [
              {
                  "text": {
                    "text": [
                  "ยืนยันการวินิฉัยโรคทั้งหมด "+str(x["c"][len(x["c"])-1])+" คำถาม"
                  ]
                  },
                  "platform": "LINE"
              },
              {
                  "text": {
                    "text": [
                  "(บริการของเราไม่ใช่คำวินิจฉัยของแพทย์ แต่เป็นเพียงการให้ข้อมูลเบื้องต้นเท่านั้น หากมีข้อสงสัย ควรปรึกษาแพทย์ผู้เชี่ยวชาญเพิ่มเติม)"
                  ]
                  },
                  "platform": "LINE"
              },
              {
                "quickReplies": {
                "title": "ยืนยันการวินิจฉัยโรค",
                "quickReplies": ["ใช่"]
              },
                "platform": "LINE"
              }
              ]
          }
    elif query_result.get('action') == "covid-analyzing":
        code = query_result.get('outputContexts')[0].get('parameters').get('code')
        x = json.loads(code)
        print(x)
        if query_result.get('queryText') == "ใช่":
          if  x["c"][len(x["c"])-1] == x["c"][len(x["c"])-2]:
              x["c"][1+x["c"][len(x["c"])-3]] = x["c"][1+x["c"][len(x["c"])-3]]+medication_Dict[56]["Risk_Score"][9]
              temp = ""
              for i in range(0, (len(x["c"]))-3, 3):
                percent = int(x["c"][i+1]*100/17)-1
                if percent >= 100:
                    percent = 99
                elif percent < 0:
                    percent = 0
                temp += str(percent)+"% | "+medication_Dict[x["c"][i]-1]["Name"]+"\n"
              print(x)
              if x["c"][i+1] > 11:
                temp += "\nคุณมีความเสี่ยงสูงที่จะเป็น COVID-19\n*หากมีอาการหอบเหนื่อย หายใจไม่ทัน พูดไม่เป็นคำ โทรเรียกรถฉุกเฉิน 1669\nพร้อมแจ้งความเสี่ยงในการติดเชื้อ COVID-19"
              elif x["c"][i+1] > 7:
                temp += "\n'คุณมีความเสี่ยงปานกลาง' ในการได้รับเชื้อ COVID-19\n*หากมีอาการหอบเหนื่อย หายใจไม่ทัน พูดไม่เป็นคำ โทรเรียกรถฉุกเฉิน 1669\nพร้อมแจ้งความเสี่ยงในการติดเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
              elif x["c"][i+1] > 3:
                temp += "\n'คุณมีความเสี่ยงน้อย' ในการได้รับเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
              else:
                temp += "\n'คุณมีความเสี่ยงน้อยมาก' ในการได้รับเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
              return {
              "displayText": '25',
              "source": "webhookdata",
              "fulfillmentMessages": [
              {
                  "text": {
                    "text": [temp]
                  },
                  "platform": "LINE"
              }
              ]
              }
          elif x["c"][2+x["c"][len(x["c"])-3]] == len(medication_Dict[x["c"][x["c"][len(x["c"])-3]]-1]["Long_Symptom"])-1:
                x["c"][1+x["c"][len(x["c"])-3]] = x["c"][1+x["c"][len(x["c"])-3]]+medication_Dict[56]["Risk_Score"][x["c"][4]-2]
                x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]+1
                x["c"][len(x["c"])-3] = x["c"][len(x["c"])-3]+3
                x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]-1
                x["c"][1+x["c"][len(x["c"])-3]] = x["c"][1+x["c"][len(x["c"])-3]]-medication_Dict[56]["Risk_Score"][x["c"][4]-2]
          x["c"][len(x["c"])-2] = x["c"][len(x["c"])-2]+1
          x["c"][1+x["c"][len(x["c"])-3]] = x["c"][1+x["c"][len(x["c"])-3]]+medication_Dict[56]["Risk_Score"][x["c"][4]-2]
          x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]+1

        elif query_result.get('queryText') == "ไม่":
          if  x["c"][len(x["c"])-1] == x["c"][len(x["c"])-2]:
            temp = ""
            for i in range(0, (len(x["c"]))-3, 3):
              percent = int(x["c"][i+1]*100/17)-1
              if percent >= 100:
                percent = 99
              elif percent < 0:
                percent = 0
              temp += str(percent)+"% | "+medication_Dict[x["c"][i]-1]["Name"]+"\n"
            print(x)
            if x["c"][i+1] > 11:
              temp += "\nคุณมีความเสี่ยงสูงที่จะเป็น COVID-19\n*หากมีอาการหอบเหนื่อย หายใจไม่ทัน พูดไม่เป็นคำ โทรเรียกรถฉุกเฉิน 1669\nพร้อมแจ้งความเสี่ยงในการติดเชื้อ COVID-19"
            elif x["c"][i+1] > 7:
              temp += "\n'คุณมีความเสี่ยงปานกลาง' ในการได้รับเชื้อ COVID-19\n*หากมีอาการหอบเหนื่อย หายใจไม่ทัน พูดไม่เป็นคำ โทรเรียกรถฉุกเฉิน 1669\nพร้อมแจ้งความเสี่ยงในการติดเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
            elif x["c"][i+1] > 3:
              temp += "\n'คุณมีความเสี่ยงน้อย' ในการได้รับเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
            else:
              temp += "\n'คุณมีความเสี่ยงน้อยมาก' ในการได้รับเชื้อ COVID-19\nวิธีปฎิบัติตัวในช่วงของการระบาด COVID-19\n1. หมั่นล้างมือให้สะอาดด้วยสบู่หรือแอลกอฮอล์เจล\n2. หลีกเลี่ยงการสัมผัสผู้ที่มีอาการคล้ายไข้หวัด หรือหลีกเลี่ยงการไปที่มีฝูงชน\n3. ปรุงอาหารประเภทเนื้อสัตว์และไข่ให้สุกด้วยความร้อน\n4. ให้ผ้าปิดปากหรือจมูก เพื่อป้องกันการได้รับเชื้อโรค"
            return {
              "displayText": '25',
              "source": "webhookdata",
              "fulfillmentMessages": [
              {
                  "text": {
                    "text": [temp]
                  },
                  "platform": "LINE"
              }
              ]
              }
          elif x["c"][2+x["c"][len(x["c"])-3]] == len(medication_Dict[x["c"][x["c"][len(x["c"])-3]]-1]["Long_Symptom"])-1:
                x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]+1
                x["c"][len(x["c"])-3] = x["c"][len(x["c"])-3]+3
                x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]-1
          x["c"][len(x["c"])-2] = x["c"][len(x["c"])-2]+1
          x["c"][2+x["c"][len(x["c"])-3]] = x["c"][2+x["c"][len(x["c"])-3]]+1
        symptom = x["c"][x["c"][len(x["c"])-3]]-1
        question = x["c"][2+x["c"][len(x["c"])-3]]
        q = medication_Dict[symptom]["Long_Symptom"][question]
        temp = str(x["c"][len(x["c"])-2])+"/"+str(x["c"][len(x["c"])-1])+" | "+q
        code_rewrite = ""
        for i in str(x):
          if i == " ":
            continue
          elif i == "\'":
            code_rewrite += "\""
          else:
            code_rewrite += i
        print(code_rewrite)
        return {
              "displayText": '25',
              "source": "webhookdata",
              "outputContexts" : [
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/covid_starter",
                  "lifespanCount" : (int(x["c"][len(x["c"])-1])-int(x["c"][len(x["c"])-2]))+1,
                  "parameters" : {
                    "code" : code_rewrite
                  }
                }
              ],
              "fulfillmentMessages": [
              {
                  "text": {
                    "text": [temp]
                  },
                  "platform": "LINE"
              },
              {
                "quickReplies": {
                "title": "ใช่หรือไม่",
                "quickReplies": ["ใช่", "ไม่"]
              },
                "platform": "LINE"
              }
              ]
          }
    elif query_result.get('action') == "sad-starter":
        code = '{"c":[107,0,0,9]}'
        x = json.loads(code)
        print(x)
        code_rewrite = ""
        for i in str(x):
            if i == " ":
                continue
            elif i == "\'":
                code_rewrite += "\""
            else:
                code_rewrite += i
        return {
            "displayText": '25',
            "source": "webhookdata",
            "outputContexts" : [{
                "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/sad_analyzing",
                "lifespanCount" : 9,
                "parameters" : {
                  "code" : code_rewrite
                }
            }],
            "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                    "ยืนยันการวินิจฉัยโรคทั้งหมด 9 คำถาม"
                    ]
                },
                "platform": "LINE"
            },
            {
                "text": {
                    "text": [
                    "(บริการของเราไม่ใช่คำวินิจฉัยของแพทย์ แต่เป็นเพียงการให้ข้อมูลเบื้องต้นเท่านั้น หากมีข้อสงสัย ควรปรึกษาแพทย์ผู้เชี่ยวชาญเพิ่มเติม)"
                    ]
                },
                "platform": "LINE"
            },
            {
                "quickReplies": {
                "title": "ยืนยันการวินิจฉัยโรค",
                "quickReplies": ["ใช่"]
            },
                "platform": "LINE"
            }
            ]
        }

    elif query_result.get('action') == "sad-analyzing":
        code = query_result.get('outputContexts')[0].get('parameters').get('code')
        x = json.loads(code)
        if query_result.get('queryText') == "ใช่":
            code_rewrite = ""
            for i in str(x):
                if i == " ":
                    continue
                elif i == "\'":
                    code_rewrite += "\""
                else:
                    code_rewrite += i
            return {
                "displayText": '25',
                "source": "webhookdata",
                "outputContexts" : [{
                    "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/sad_analyzing",
                    "lifespanCount" : 8,
                    "parameters" : {"code" : code_rewrite}
                }],
                "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["ในช่วง 2 สัปดาห์ที่ผ่านมา รวมทั้งวันนี้ ท่านมีอาการ"]
                    },
                    "platform": "LINE"
                },
                {
                    "text": {
                        "text": ["1/9 | "+medication_Dict[106]["Long_Symptom"][0]+"หรือไม่ ?"]
                    },
                    "platform": "LINE"
                },
                {
                    "quickReplies": {
                    "title": "เลือกคำตอบด้านล่างนี้",
                    "quickReplies": ["ไม่มีเลย", "เป็นบางวัน", "เป็นบ่อย", "เป็นทุกวัน"]
                },
                    "platform": "LINE"
                }
                ]
            }
        elif query_result.get('queryText') == "เป็นทุกวัน":
            if x["c"][2] == x["c"][3]-1:
                x["c"][1] += 3
                percent = int(x["c"][1]*100/27)-1
                if percent >= 100:
                    percent = 99
                elif percent < 0:
                    percent = 0
                temp = str(percent)+"% | โรคซึมเศร้า\n"
                if x["c"][1] > 18:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับรุนแรง"
                    temp += "\nควรปรึกษาจิตแพทย์"
                elif x["c"][1] > 12:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับปานกลาง"
                    temp += "\nควรปรึกษาจิตแพทย์"
                elif x["c"][1] > 6:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับน้อย"
                else:
                    temp += "\nไม่มีอาการของโรคซึมเศร้า หรือมีอาการของโรคซึมเศร้า ระดับน้อยมาก"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [temp]
                        },
                        "platform": "LINE"
                    }
                    ]
                }
            else:
                x["c"][1] += 3
                x["c"][2] += 1
        elif query_result.get('queryText') == "เป็นบ่อย":
            if x["c"][2] == x["c"][3]-1:
                x["c"][1] += 2
                percent = int(x["c"][1]*100/27)-1
                if percent >= 100:
                    percent = 99
                elif percent < 0:
                    percent = 0
                temp = str(percent)+"% | โรคซึมเศร้า\n"
                if x["c"][1] > 18:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับรุนแรง"
                    temp += "\nควรปรึกษาจิตแพทย์"
                elif x["c"][1] > 12:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับปานกลาง"
                    temp += "\nควรปรึกษาจิตแพทย์"
                elif x["c"][1] > 6:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับน้อย"
                else:
                    temp += "\nไม่มีอาการของโรคซึมเศร้า หรือมีอาการของโรคซึมเศร้า ระดับน้อยมาก"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [temp]
                        },
                        "platform": "LINE"
                    }
                    ]
                }
            else:
                x["c"][1] += 2
                x["c"][2] += 1
        elif query_result.get('queryText') == "เป็นบางวัน":
            if x["c"][2] == x["c"][3]-1:
                x["c"][1] += 1
                percent = int(x["c"][1]*100/27)-1
                if percent >= 100:
                    percent = 99
                elif percent < 0:
                    percent = 0
                temp = str(percent)+"% | โรคซึมเศร้า\n"
                if x["c"][1] > 18:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับรุนแรง"
                    temp += "\nควรปรึกษาจิตแพทย์"
                elif x["c"][1] > 12:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับปานกลาง"
                    temp += "\nควรปรึกษาจิตแพทย์"
                elif x["c"][1] > 6:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับน้อย"
                else:
                    temp += "\nไม่มีอาการของโรคซึมเศร้า หรือมีอาการของโรคซึมเศร้า ระดับน้อยมาก"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [temp]
                        },
                        "platform": "LINE"
                    }
                    ]
                }
            else:
                x["c"][1] += 1
                x["c"][2] += 1
        elif query_result.get('queryText') == "ไม่มีเลย":
            if x["c"][2] == x["c"][3]-1:
                percent = int(x["c"][1]*100/27)-1
                if percent >= 100:
                    percent = 99
                elif percent < 0:
                    percent = 0
                temp = str(percent)+"% | โรคซึมเศร้า\n"
                if x["c"][1] > 18:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับรุนแรง"
                    temp += "\nควรปรึกษาจิตแพทย์"
                elif x["c"][1] > 12:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับปานกลาง"
                    temp += "\nควรปรึกษาจิตแพทย์"
                elif x["c"][1] > 6:
                    temp += "\nคุณมีอาการของโรคซึมเศร้า ระดับน้อย"
                else:
                    temp += "\nไม่มีอาการของโรคซึมเศร้า หรือมีอาการของโรคซึมเศร้า ระดับน้อยมาก"
                return {
                    "displayText": '25',
                    "source": "webhookdata",
                    "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [temp]
                        },
                        "platform": "LINE"
                    }
                    ]
                }
            else:
                x["c"][2] += 1
        code_rewrite = ""
        for i in str(x):
            if i == " ":
                continue
            elif i == "\'":
                code_rewrite += "\""
            else:
                code_rewrite += i
        return {
            "displayText": '25',
            "source": "webhookdata",
            "outputContexts" : [{
                "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/sad_analyzing",
                "lifespanCount" : (x["c"][3]-x["c"][2]),
                "parameters" : {
                    "code" : code_rewrite
                }
            }],
            "fulfillmentMessages": [
            {
                "text": {
                    "text": [str(x["c"][2]+1)+"/"+str(x["c"][3])+" | "+medication_Dict[106]["Long_Symptom"][x["c"][2]]]
                },
                "platform": "LINE"
            },
            {
                "quickReplies": {
                "title": "ใช่หรือไม่",
                "quickReplies": ["ไม่มีเลย", "เป็นบางวัน", "เป็นบ่อย", "เป็นทุกวัน"]
            },
                "platform": "LINE"
            }
            ]
        }

    elif query_result.get('action') == "reset-context":
        return {
            "displayText": '25',
            "source": "webhookdata",
            "outputContexts" : [
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/analyze_starter",
                  "lifespanCount" : -1,
                },
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/covid_starter",
                  "lifespanCount" : -1,
                },
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/analyze-3-symptom",
                  "lifespanCount" : -1,
                },
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/sad_analyzing",
                  "lifespanCount" : -1,
                },
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/code_analyze",
                  "lifespanCount" : -1,
                },
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/sad_starter",
                  "lifespanCount" : -1,
                },
                {
                  "name" : "projects/doctor-tanjai-aubr/agent/sessions/df70f41c-d459-9d85-fb96-b09795fda20f/contexts/sad_analyzing",
                  "lifespanCount" : -1,
                }
            ],
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["ทำการรีเซ็ตระบบเรียบร้อย"]
                    },
                    "platform": "LINE"
                }
            ]
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

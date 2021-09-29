import React from "react";
import {Layout, Table, Tag} from "antd";
import axios from "axios";
import {simpleDuration} from "../common";

const { Content,Header } = Layout;
class AllTask extends React.Component{
  constructor(props) {
    super(props);
    this.columns = [
      {
        title: "test_id",
        dataIndex: "test_id",
        key: "test_id",
        // render: (text) => <a>{text}</a>,
      },
      {
        title: "测试类型",
        dataIndex: "type",
        key: "type",
      },
      {
        title: "测试环境",
        dataIndex: "env_type",
        key: "env_type",
      },
      {
        title: "状态",
        dataIndex: "status",
        key: "status",
        render: (text,record)=>{
          let color;
          switch (text) {
            case 2:
              color = 'success';
              text = "成功"
              break;
            case -2:
              color = 'warning';
              text = "人为终止"
              break;
            default:
              color = 'error';
              text = "失败"
              break;
          }
          return <Tag color={color}>{text}</Tag>
        }

      },
      {
        title: "启动人",
        key: "people",
        dataIndex: "people",
      },
      {
        title: "启动时间",
        key: "start_time",
        dataIndex: "start_time",
      },
      {
        title: "总耗时 (s)",
        key: "during",
        dataIndex: "during",
      },
    ];
    this.handleChangePage = this.handleChangePage.bind(this);
    this.state = {data:null,current_page:1, total:0, pageSize:10, loading:false};
  }
  componentDidMount() {
    this.request_data();
  }

  datetimeHandle(date_str){
    const time = new Date(date_str);
    // time.setHours(time.getHours()+8)
    return time.toString()
  }

  formatDatav2(data){
    let data2 = [];
    data.detail.forEach((item, index, array)=>{
      let obj = {};
      let req_params = JSON.parse(item.req_params)
      obj["key"] = index;
      obj["uuid"] = item.id;
      obj["test_id"] = item.id;
      obj["type"] = item.test_type;
      obj["env_type"] = item.env
      obj["status"] = item.status;
      obj["people"] = req_params?req_params.email:null;
      obj["start_time"] = item.create_time;
      obj["during"] = simpleDuration(item.during,'s');
      // obj["during"] = item.during;
      if (!item.during){
        console.log(simpleDuration(item.during,'s'))
        console.log(typeof obj["during"])
      }
      data2.push(obj);
    })
    return data2
  }
  request_data(page=1,pageSize=10){
    let uri = '/uwsgi/ai_info/get_all_tasks/v2';
    this.setState({loading:true})
    axios.get(uri,{params:{page:page,page_nums:pageSize}}).then(
        (response)=>{
          let data = this.formatDatav2(response.data.data)
          this.setState({data:data,total:response.data.data.total,loading:false})
        }
    )
  }
  handleChangePage(page, pageSize){
    this.request_data(page,pageSize);
    this.setState({current_page:page,pageSize:pageSize})
  }
  render() {
    return (
        <Layout>
          <Content>
            <Table
                columns={this.columns}
                dataSource={this.state.data}
                pagination={{pageSize:this.state.pageSize, total:this.state.total,onChange:this.handleChangePage}}
                loading={this.state.loading}
            />
          </Content>
        </Layout>
        )
  }

}
export default AllTask
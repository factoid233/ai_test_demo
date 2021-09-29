/**
 *用于将时间段人性化展示成易读的形式
 * **/
export function simpleDuration(duration, type) {
    if (!duration){
        return '-'
    }
    if (type === 's') {
        duration = duration * 1000
    }
    let days = '', hours = '', minutes = '', seconds = ''
    let day = 24 * 60 * 60 * 1000,
        hour = 60 * 60 * 1000,
        minute = 60 * 1000,
        second = 1000
    if (duration >= day) {
        days = Math.floor(duration / day) + '天'
        hours = Math.floor(duration % day / hour) + '小时'
    } else if (duration >= hour && duration < day) {
        hours = Math.floor(duration / hour) + '小时'
        minutes = Math.floor(duration % hour / minute) + '分钟'
    } else if (duration > minute && duration < hour) {
        minutes = Math.floor(duration / minute) + '分钟'
        seconds = Math.floor(duration % minute / second) + '秒'
    } else if (duration <= minute) {
        seconds = Math.floor(duration / second) + '秒'
    }
    return days + hours + minutes + seconds
}
/**
 * @date:
 *用于将日期字符串 格式化展示成 1997-01-01 00:00:00的形式
**/
export function formatDateTime(date) {
  let d = new Date(date),
      //格式化日期
      month = "" + (d.getMonth() + 1),
      day = "" + d.getDate(),
      year = d.getFullYear();

  if (month.length < 2) month = "0" + month;
  if (day.length < 2) day = "0" + day;
  let _date = [year, month, day].join("-");

  //格式化时间
  let hour = "" + d.getHours(), minute = "" + d.getMinutes(), second = "" + d.getSeconds();
  let temp = [hour, minute, second]
  temp.forEach((item,index,array)=>{
        if (item.length < 2){
          array[index] = '0' + item;
        }
      }
  )
  let _time = temp.join(':');
  return _date + ' ' + _time;
}


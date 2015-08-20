require 'rubygems'
require 'bundler/setup'
require 'open3'
require 'pathname'
require 'open-uri'
require 'json'
require 'yaml'
require 'chatterbot/dsl'

config = YAML.load_file('FluffyHaiiro.yaml')
consumer_key config[:consumer_key]
consumer_secret config[:consumer_secret]
secret config[:secret]
token config[:token]

ROOT_ABSOLUTE_PATH = Dir.pwd
#search("cat", limit: 10) do |tweet|
	#retweet tweet.id
#end

#client.user_search('cat', {count: 10, page:1}).each do |user|
#	follow user
#end

imgUrl = 'http://sv6.postjung.com/picpost/data/177/177362-7-6387.jpg'

imgFolderPath = ROOT_ABSOLUTE_PATH + '/images'
timestamp = Time.now.getutc.to_i
imgPath = imgFolderPath + '/' + timestamp.to_s + '.jpg'

File.open(imgPath, 'wb') do |f|
	f.write(open(imgUrl).read)
end

#turn off google logging
caffeCmd = 'GLOG_minloglevel=1 python categorize.py ' + imgPath
puts caffeCmd 
predictedCategories = nil
Open3.popen3(caffeCmd){|stdin, stdout, stderr, wait_thr|
	predictedCategories = JSON.parse(stdout.read)
	stdin.close
	stdout.close
	stderr.close
}

predictedCategories.map!{|c| c.split(' ', 2).last}
p predictedCategories

require 'rubygems'
require 'bundler/setup'
require 'open3'
require 'pathname'
require 'open-uri'
require 'json'
require 'yaml'
require 'chatterbot/dsl'
require 'fastimage'

config = YAML.load_file('FluffyHaiiro.yaml')
consumer_key config[:consumer_key]
consumer_secret config[:consumer_secret]
secret config[:secret]
token config[:token]

ROOT_ABSOLUTE_PATH = Dir.pwd
IMG_FOLDER_PATH = ROOT_ABSOLUTE_PATH + '/images'
VALID_IMG_TYPES = [:png, :jpeg]
CLASSIFIER_MAIN_PATH  = ROOT_ABSOLUTE_PATH + '/classifier/Classify.py'
RESULT_PATH = ROOT_ABSOLUTE_PATH + '/result.json'
#search("cat", limit: 10) do |tweet|
	#retweet tweet.id
#end

#client.user_search('cat', {count: 10, page:1}).each do |user|
#	follow user
def isValidImageType imgUrl
	begin
		type = FastImage.type(imgUrl, raise_on_failure: true)
		return VALID_IMG_TYPES.include? type
	rescue Exception => e 
		puts e.message
		false
	end
end

def isSizeLargeEnough imgUrl
	begin
		puts imgUrl
		size = FastImage.size(imgUrl, raise_on_failure: true)
		aspect_ratio = size[1] / [size[0], 0].max.to_f
		return aspect_ratio >= 0.25 && aspect_ratio <= 4
	rescue Exception => e
		puts e.message
		false
	end
end

def categorize imgUrl
	#check if image is valid type
	if !isValidImageType(imgUrl) then return nil end
	#check if size is large enough
	if !isSizeLargeEnough(imgUrl) then return nil end

	caffeCmd = 'GLOG_minloglevel=1 python ' + CLASSIFIER_MAIN_PATH + ' ' + imgUrl
	puts imgUrl
	system caffeCmd
end

search("cute cat", {limit: 10, inluded_entities: true}) do |t|
	if t.media?
		t.media.each do |m|
			imgUrl =  m.media_url_https.to_s
			categorize imgUrl
			result = JSON.parse(IO.read(RESULT_PATH))
			p result

			result.each do |entry|
				#category
				category = entry[0]
				confidence = entry[1].to_f
				containsCat = category.include? ' cat' || category ==  'cat'
				if containsCat && confidence >  0.8
					retweet t
					puts 'retweeted'
					break
				end
			end
		end
	end
end
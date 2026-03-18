module Blog
  class Post
    attr_accessor :title, :body, :author, :tags

    def initialize(title, body, author)
      @title = title
      @body = body
      @author = author
      @tags = []
      @published_at = nil
    end

    def publish
      @published_at = Time.now
    end

    def published?
      !@published_at.nil?
    end

    def add_tag(tag)
      @tags << tag unless @tags.include?(tag)
    end

    def summary(length = 100)
      body.length > length ? body[0...length] + "..." : body
    end
  end

  class Blog
    attr_reader :name, :posts

    def initialize(name)
      @name = name
      @posts = []
    end

    def add_post(post)
      @posts << post
    end

    def published_posts
      @posts.select(&:published?)
    end

    def find_by_tag(tag)
      @posts.select { |p| p.tags.include?(tag) }
    end

    def self.create(name)
      new(name)
    end
  end
end
